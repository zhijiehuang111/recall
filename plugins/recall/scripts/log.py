# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
"""在 Vault 的 `recall/reviews.jsonl` 追加一筆事件。

用法：uv run log.py review <card-id> --grade again|hard|good|easy --hints N [--at ISO8601] [--vault 路徑]
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

from recall_core import (
    GRADES,
    VaultError,
    append_event,
    card_exists,
    fail,
    find_recall_dir,
    parse_timestamp,
    read_events,
    schedule,
)


def _timestamp(value: str) -> datetime:
    try:
        return parse_timestamp(value)
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--vault", type=Path, default=Path.cwd(), help="Vault 根目錄（預設為目前目錄）"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    review = commands.add_parser("review", help="記錄一次作答")
    review.add_argument("card", help="Card ID（cards/ 下的檔名，不含 .md）")
    review.add_argument("--grade", required=True, choices=GRADES)
    review.add_argument("--hints", required=True, type=_hints, help="用了幾次 Hint")
    review.add_argument(
        "--at", type=_timestamp, help="作答時間，ISO 8601 含時區（預設為現在）"
    )
    args = parser.parse_args()

    try:
        recall = find_recall_dir(args.vault)
        if not card_exists(recall, args.card):
            raise VaultError(f"找不到卡片 {recall}/cards/{args.card}.md，未寫入紀錄。")
        # 先確認既有紀錄讀得懂，才寫入；壞掉的紀錄要先修好。
        events = read_events(recall)
    except VaultError as err:
        fail(err)

    at = args.at or datetime.now().astimezone()
    event = {
        "event": "review",
        "card": args.card,
        "at": at.isoformat(timespec="seconds"),
        "grade": args.grade,
        "hints": args.hints,
    }
    append_event(recall, event)
    due = schedule([*events, event])[args.card].due
    print(json.dumps({"card": args.card, "due": due.isoformat()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
