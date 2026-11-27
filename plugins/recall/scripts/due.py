# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
"""列出今天要考的卡，依考試順序輸出 JSON。

到期的卡（review）一律列出：上次 Again / Hard 的先，其餘逾期越久越前。
從未作答的新卡（new）依 created 先後，放得進 `config.toml` 的 `daily_minutes`
剩餘預算才加。預估分鐘：Recall 3、Explain 5、Build 30。
`notes` 是自最近一次 reset 以來最近 3 筆作答 note，最新的在前。

用法：uv run due.py [--vault 路徑] [--today YYYY-MM-DD]
"""

import argparse
import json
from datetime import date
from pathlib import Path

from recall_core import (
    Card,
    CardState,
    VaultError,
    fail,
    find_recall_dir,
    read_cards,
    read_daily_minutes,
    read_events,
    recent_notes,
    schedule,
)

# 各類型卡片預估要花幾分鐘，用來計入每日預算。
MINUTES = {"recall": 3, "explain": 5, "build": 30}


def _minutes(card: Card) -> int:
    # type 缺漏或拼錯的卡照 Recall 估，不讓一張壞卡擋掉整個 Session。
    return MINUTES.get(card.type or "", MINUTES["recall"])


def _entry(card: Card, state: CardState | None, notes: list[str]) -> dict:
    if state is None:
        kind, due, lapses, leech = "new", card.created, 0, False
    else:
        kind, due, lapses, leech = "review", state.due, state.lapses, state.leech
    return {
        "card": card.id,
        "type": card.type,
        "kind": kind,
        "minutes": _minutes(card),
        "due": due and due.isoformat(),
        "lapses": lapses,
        "leech": leech,
        "notes": notes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--vault", type=Path, default=Path.cwd(), help="Vault 根目錄（預設為目前目錄）"
    )
    parser.add_argument(
        "--today",
        type=date.fromisoformat,
        default=date.today(),
        help="把哪一天當作今天（YYYY-MM-DD，預設為本地今天）",
    )
    args = parser.parse_args()

    try:
        recall = find_recall_dir(args.vault)
        daily_minutes = read_daily_minutes(recall)
        events = read_events(recall)
    except VaultError as err:
        fail(err)
    states = schedule(events)
    notes = recent_notes(events)

    due_cards: list[tuple[Card, CardState]] = []
    new_cards: list[Card] = []
    for card in read_cards(recall):
        state = states.get(card.id)
        if state is None:
            new_cards.append(card)
        elif state.due <= args.today:
            due_cards.append((card, state))

    # 上次出錯（Again / Hard）的到期卡先考，其餘到期卡逾期越久越前。
    due_cards.sort(
        key=lambda pair: (
            pair[1].last_grade not in ("again", "hard"),
            pair[1].due,
            pair[0].id,
        )
    )
    reviews = [_entry(card, state, notes.get(card.id, [])) for card, state in due_cards]

    # 到期卡一律列出（即使超出預算）；新卡依 created 先後，放得進剩餘預算才加，
    # 放不下的跳過、繼續往後找。沒寫 created 的新卡排最後。
    cards = reviews
    planned = sum(c["minutes"] for c in reviews)
    new_cards.sort(key=lambda c: (c.created is None, c.created or args.today, c.id))
    for card in new_cards:
        if planned + _minutes(card) <= daily_minutes:
            cards.append(_entry(card, None, []))
            planned += _minutes(card)

    print(
        json.dumps(
            {
                "today": args.today.isoformat(),
                "budget": {"daily_minutes": daily_minutes, "planned_minutes": planned},
                "cards": cards,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
