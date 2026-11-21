# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
"""列出今天要考的卡：從未作答的新卡（new）與已到期的卡（review），輸出 JSON。

用法：uv run due.py [--vault 路徑] [--today YYYY-MM-DD]
"""

import argparse
import json
from datetime import date
from pathlib import Path

from recall_core import (
    Card,
    VaultError,
    fail,
    find_recall_dir,
    read_cards,
    read_events,
    schedule,
)


def _entry(card: Card, kind: str, due: date | None) -> dict:
    return {
        "card": card.id,
        "type": card.type,
        "kind": kind,
        "due": due and due.isoformat(),
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
        states = schedule(read_events(recall))
    except VaultError as err:
        fail(err)

    cards = []
    for card in read_cards(recall):
        state = states.get(card.id)
        if state is None:
            cards.append(_entry(card, "new", card.created))
        elif state.due <= args.today:
            cards.append(_entry(card, "review", state.due))
    print(
        json.dumps(
            {"today": args.today.isoformat(), "cards": cards}, ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()
