"""`due` 與 `log` 共用的 Vault 資料存取。只用標準函式庫。

資料契約見 repo 的 docs/design.md 與 ADR 0001：`reviews.jsonl` 是排程的唯一真相來源，
排程狀態每次重播算出、不落地。
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

# 腳本只讀這幾個 frontmatter 欄位，且只認單行 `key: value`；其餘行一律略過。
_FIELD = re.compile(r"^(type|created|topic|capstone):[ \t]*(.*?)[ \t]*$")

GRADES = ("again", "hard", "good", "easy")


class VaultError(Exception):
    """使用者看得懂的錯誤；由腳本印到 stderr 並以非零狀態結束。"""


def parse_timestamp(value: str) -> datetime:
    """解析 ISO 8601 時間；必須含時區。"""
    try:
        at = datetime.fromisoformat(value)
    except ValueError:
        raise ValueError(f"不是 ISO 8601 時間：{value}") from None
    if at.tzinfo is None:
        raise ValueError(f"時間缺少時區（例如 +08:00）：{value}")
    return at


def find_recall_dir(vault: Path) -> Path:
    recall = vault / "recall"
    if not recall.is_dir():
        raise VaultError(f"找不到 {recall}/：請在 Vault 根目錄執行，或用 --vault 指定 Vault 根目錄。")
    return recall


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
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as err:
            raise VaultError(f"{path} 第 {number} 行不是合法的 JSON：{err.msg}") from err
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
        parse_timestamp(at)
    except ValueError as err:
        return f"at {err}"
    return None


@dataclass(frozen=True)
class CardState:
    due: date


def schedule(events: list[dict]) -> dict[str, CardState]:
    """依序重播事件，算出每張作答過的卡目前的排程狀態；沒出現在結果裡的卡就是新卡。

    排程演算法只藏在這裡。目前是 tracer bullet 規則：任何作答後隔天到期。
    """
    states: dict[str, CardState] = {}
    for event in events:
        if event.get("event") != "review":
            continue
        reviewed_on = local_date(event["at"])
        states[event["card"]] = CardState(due=reviewed_on + timedelta(days=1))
    return states


def local_date(at: str) -> date:
    """`at`（ISO 8601 含時區）換算成本地時區的日期；本地午夜換日。"""
    return datetime.fromisoformat(at).astimezone().date()


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


def fail(err: VaultError) -> None:
    print(err, file=sys.stderr)
    sys.exit(1)
