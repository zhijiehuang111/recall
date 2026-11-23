# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
"""在 Vault 的 `recall/reviews.jsonl` 追加一筆事件。

用法：
  uv run log.py [--vault 路徑] review <card-id> --grade again|hard|good|easy --hints N [--at 2026-11-03]
  uv run log.py [--vault 路徑] reset <card-id> [--at 2026-11-03]

`--vault` 是所有子指令共用的選項，要寫在子指令前面。

成功時輸出 JSON：`due` 是這張卡下次到期日；reset 之後卡片視為新卡，`due` 為 null。
"""

import argparse
import json
from datetime import date
from pathlib import Path

from recall_core import (
    GRADES,
    VaultError,
    append_event,
    card_exists,
    fail,
    find_recall_dir,
    parse_day,
    read_events,
    schedule,
)


def _day(value: str) -> date:
    try:
        return parse_day(value)
    except ValueError as err:
        raise argparse.ArgumentTypeError(str(err)) from None


def _hints(value: str) -> int:
    try:
        n = int(value)
    except ValueError:
        n = -1
    if n < 0:
        raise argparse.ArgumentTypeError(f"Hint 次數必須是 0 以上的整數：{value}")
    return n


def _add_card_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("card", help="Card ID（cards/ 下的檔名，不含 .md）")


def _add_at_argument(parser: argparse.ArgumentParser, what: str) -> None:
    parser.add_argument("--at", type=_day, help=f"{what}，YYYY-MM-DD（預設為今天）")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--vault", type=Path, default=Path.cwd(), help="Vault 根目錄（預設為目前目錄）"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    review = commands.add_parser("review", help="記錄一次作答")
    _add_card_argument(review)
    review.add_argument("--grade", required=True, choices=GRADES)
    review.add_argument("--hints", required=True, type=_hints, help="用了幾次 Hint")
    _add_at_argument(review, "作答日期")

    reset = commands.add_parser(
        "reset", help="重置一張卡的排程；之前的紀錄保留，但不再計入"
    )
    _add_card_argument(reset)
    _add_at_argument(reset, "重置日期")
    args = parser.parse_args()

    try:
        recall = find_recall_dir(args.vault)
        if not card_exists(recall, args.card):
            raise VaultError(f"找不到卡片 {recall}/cards/{args.card}.md，未寫入紀錄。")
        # 先確認既有紀錄讀得懂，才寫入；壞掉的紀錄要先修好。
        events = read_events(recall)
    except VaultError as err:
        fail(err)

    at = args.at or date.today()
    event = {
        "event": args.command,
        "card": args.card,
        "at": at.isoformat(),
    }
    if args.command == "review":
        event |= {"grade": args.grade, "hints": args.hints}
    append_event(recall, event)
    state = schedule([*events, event]).get(args.card)
    due = state and state.due.isoformat()
    print(json.dumps({"card": args.card, "due": due}, ensure_ascii=False))


if __name__ == "__main__":
    main()
