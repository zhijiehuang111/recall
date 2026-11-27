"""plugin 腳本共用的 Vault 資料存取與錯誤處理。只用標準函式庫。

資料契約見 repo 的 docs/design.md 與 ADR 0001：`reviews.jsonl` 是排程的唯一真相來源，
排程狀態每次重播算出、不落地。
"""

import json
import math
import re
import sys
import tomllib
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import NoReturn

# 腳本只讀這幾個 frontmatter 欄位，且只認單行 `key: value`；其餘行一律略過。
_FIELD = re.compile(r"^(type|created|topic|capstone):[ \t]*(.*?)[ \t]*$")

GRADES = ("again", "hard", "good", "easy")


class VaultError(Exception):
    """使用者看得懂的錯誤；由腳本印到 stderr 並以非零狀態結束。"""


_DAY = re.compile(r"\d{4}-\d{2}-\d{2}")


def parse_day(value: str) -> date:
    """解析 `YYYY-MM-DD` 日期；紀錄只記日期，不記時間與時區。"""
    try:
        if _DAY.fullmatch(value):
            return date.fromisoformat(value)
    except ValueError:
        pass
    raise ValueError(f"不是 YYYY-MM-DD 日期：{value}")


def find_recall_dir(vault: Path) -> Path:
    recall = vault / "recall"
    if not recall.is_dir():
        raise VaultError(
            f"找不到 {recall}/：請在 Vault 根目錄執行，或用 --vault 指定 Vault 根目錄。"
        )
    return recall


DEFAULT_DAILY_MINUTES = 30


def read_daily_minutes(recall: Path) -> int:
    """`config.toml` 的 `daily_minutes`；沒有設定檔或沒寫這個欄位時用預設值。"""
    path = recall / "config.toml"
    if not path.exists():
        return DEFAULT_DAILY_MINUTES
    try:
        config = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as err:
        raise VaultError(f"{path} 不是合法的 TOML：{err}") from err
    minutes = config.get("daily_minutes", DEFAULT_DAILY_MINUTES)
    # bool 是 int 的子類別，`daily_minutes = true` 也要擋下來。
    if not isinstance(minutes, int) or isinstance(minutes, bool) or minutes < 0:
        raise VaultError(f"{path} 的 daily_minutes 必須是 0 以上的整數：{minutes!r}")
    return minutes


@dataclass(frozen=True)
class Card:
    id: str
    type: str | None
    created: date | None
    topic: str | None
    capstone: bool


def card_exists(recall: Path, card_id: str) -> bool:
    return (recall / "cards" / f"{card_id}.md").is_file()


def read_cards(recall: Path) -> list[Card]:
    cards_dir = recall / "cards"
    if not cards_dir.is_dir():
        return []
    return [_read_card(path) for path in sorted(cards_dir.glob("*.md"))]


def _read_card(path: Path) -> Card:
    fields = _frontmatter_fields(path.read_text(encoding="utf-8"))
    return Card(
        id=path.stem,
        type=fields.get("type"),
        created=_parse_date(fields.get("created")),
        topic=fields.get("topic"),
        capstone=fields.get("capstone") == "true",
    )


def _frontmatter_fields(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = _FIELD.match(line)
        if match and match.group(2):
            fields[match.group(1)] = _unquote(match.group(2))
    return fields


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def _parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _log_path(recall: Path) -> Path:
    return recall / "reviews.jsonl"


# 腳本認得、會用到的事件；其他 event 類型原樣保留在檔案裡，重播時略過。
_KNOWN_EVENTS = ("review", "reset")


def read_events(recall: Path) -> list[dict]:
    """讀出 `reviews.jsonl` 裡認得的事件；認得的事件欄位壞掉時報出是第幾行。"""
    path = _log_path(recall)
    if not path.exists():
        return []
    events = []
    for number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as err:
            raise VaultError(
                f"{path} 第 {number} 行不是合法的 JSON：{err.msg}"
            ) from err
        if not isinstance(event, dict):
            raise VaultError(f"{path} 第 {number} 行不是 JSON 物件")
        if event.get("event") not in _KNOWN_EVENTS:
            continue
        problem = _event_problem(event)
        if problem:
            raise VaultError(f"{path} 第 {number} 行：{problem}")
        events.append(event)
    return events


def _event_problem(event: dict) -> str | None:
    if not isinstance(event.get("card"), str):
        return "缺少字串欄位 card"
    at = event.get("at")
    if not isinstance(at, str):
        return "缺少字串欄位 at"
    try:
        parse_day(at)
    except ValueError as err:
        return f"at {err}"
    if event["event"] == "review":
        if event.get("grade") not in GRADES:
            return f"grade 必須是 {'、'.join(GRADES)} 之一：{event.get('grade')}"
        if not isinstance(event.get("note", ""), str):
            return "note 必須是字串"
        if not isinstance(event.get("placement", False), bool):
            return "placement 必須是 true 或 false"
    return None


@dataclass(frozen=True)
class CardState:
    reviewed_on: date
    due: date
    interval: int
    ease: float
    reviews: int
    lapses: int
    # 最近一次計入排程的 Grade（同日再考不算）。
    last_grade: str

    @property
    def leech(self) -> bool:
        return self.lapses >= LEECH_LAPSES


def schedule(events: list[dict]) -> dict[str, CardState]:
    """依序重播事件，算出每張作答過的卡目前的排程狀態；沒出現在結果裡的卡就是新卡。

    input：`reviews.jsonl` 每一行讀成的 dict，照檔案順序：
        [
            {"event": "review", "card": "sql-having", "at": "2026-11-01",
             "grade": "good", "hints": 0},
            ...
        ]
    output：Card ID → 這張卡目前的 `CardState`。
        {
            "sql-having": CardState(
            ...
            ),
        }
    """
    states: dict[str, CardState] = {}
    for event in events:
        if event["event"] == "reset":
            states.pop(event["card"], None)
            continue
        card, reviewed_on = event["card"], date.fromisoformat(event["at"])
        state = states.get(card)
        # 同一天只算第一次作答；之後的再考照樣留在紀錄裡，但不影響排程。
        if state is not None and state.reviewed_on == reviewed_on:
            continue
        grade = event["grade"]
        # Placement Quiz 答得好的首次作答視同 Easy，從較長間隔起算。
        if state is None and event.get("placement") and grade in ("good", "easy"):
            grade = "easy"
        states[card] = _next_state(state, grade, reviewed_on)
    return states


LEECH_LAPSES = 3
INITIAL_EASE = 2.5
MIN_EASE = 1.3

# 每個 Grade 讓 ease 增減多少；首次作答也套用。
_EASE_DELTA = {"again": -0.2, "hard": -0.15, "good": 0.0, "easy": 0.15}


def _next_state(state: CardState | None, grade: str, reviewed_on: date) -> CardState:
    if state is None:
        interval = 4 if grade == "easy" else 1
        ease, reviews, lapses = INITIAL_EASE, 0, 0
    else:
        # 第二次作答 Good 固定 6 天，之後 × ease。
        good_interval = 6 if state.reviews == 1 else state.interval * state.ease
        if grade == "again":
            interval = 1
        elif grade == "hard":
            interval = _days(state.interval * 1.2)
        elif grade == "easy":
            # 間隔 × ease × 1.3；第二次作答時至少以 Good 的 6 天為底，不會比 Good 早到期。
            interval = _days(max(good_interval, state.interval * state.ease) * 1.3)
        else:
            interval = _days(good_interval)
        if grade != "again":
            # ease 低時 1 天 × ease 會四捨五入回 1 天；至少多 1 天，免得卡在每天考。
            interval = max(interval, state.interval + 1)
        ease, reviews, lapses = state.ease, state.reviews, state.lapses
    return CardState(
        reviewed_on=reviewed_on,
        due=reviewed_on + timedelta(days=interval),
        interval=interval,
        # ease 只以 0.05 為單位增減；取到小數兩位，避免浮點誤差影響四捨五入。
        ease=max(MIN_EASE, round(ease + _EASE_DELTA[grade], 2)),
        reviews=reviews + 1,
        lapses=lapses + (grade == "again"),
        last_grade=grade,
    )


def _days(interval: float) -> int:
    """間隔四捨五入成整數天（.5 進位），至少 1 天。"""
    return max(1, math.floor(interval + 0.5))


RECENT_NOTES = 3


def recent_notes(events: list[dict]) -> dict[str, list[str]]:
    """每張卡自最近一次 reset 以來、最近幾筆非空 `note`，最新的在前；沒有 note 的卡不出現。"""
    notes: dict[str, list[str]] = {}
    for event in events:
        if event["event"] == "reset":
            notes.pop(event["card"], None)
        elif event.get("note", "").strip():
            notes.setdefault(event["card"], []).append(event["note"])
    return {card: found[-RECENT_NOTES:][::-1] for card, found in notes.items()}


def append_event(recall: Path, event: dict) -> None:
    """在 `reviews.jsonl` 末尾追加恰好一行；既有行一律不動。"""
    path = _log_path(recall)
    line = json.dumps(event, ensure_ascii=False) + "\n"
    with path.open("a+b") as f:
        # 手動編輯過、最後一行沒換行的檔案，先補換行，避免新事件黏在舊行後面。
        f.seek(0, 2)
        if f.tell() > 0:
            f.seek(-1, 2)
            if f.read(1) != b"\n":
                line = "\n" + line
        f.write(line.encode("utf-8"))


def fail(err: VaultError) -> NoReturn:
    print(err, file=sys.stderr)
    sys.exit(1)
