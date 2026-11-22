# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
"""在 Vault 建立 `recall/` 目錄結構與預設 `config.toml`；已存在的檔案一律不動。

用法：uv run init.py [--vault 路徑]

輸出 JSON：`recall` 為 recall/ 的路徑，`created` 表示這次是否新建了 recall/。
"""

import argparse
import json
from pathlib import Path

from recall_core import VaultError, fail

DEFAULT_CONFIG = """\
# Recall 設定。改完存檔即生效。

# 每天願意花在 Session 的分鐘數；到期複習優先，剩下的才加新卡。
daily_minutes = 30

# 正在準備的職缺方向，例如 ["backend", "ai engineer"]；開新 Topic 時用來挑題。
target_roles = []

# agent 自行出題時當地圖的 roadmap；可加 JD 或題庫的網址、Vault 內的路徑。
roadmap_sources = [
  "https://roadmap.sh/backend",
  "https://roadmap.sh/full-stack",
  "https://roadmap.sh/ai-engineer",
]
"""

SUBDIRS = ("cards", "topics", ".rubrics")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--vault", type=Path, default=Path.cwd(), help="Vault 根目錄（預設為目前目錄）"
    )
    args = parser.parse_args()

    if not args.vault.is_dir():
        fail(VaultError(f"Vault 根目錄 {args.vault} 不存在，未建立任何東西。"))

    recall = args.vault / "recall"
    created = not recall.exists()
    for name in SUBDIRS:
        (recall / name).mkdir(parents=True, exist_ok=True)
    config = recall / "config.toml"
    if not config.exists():
        config.write_text(DEFAULT_CONFIG, encoding="utf-8")
    print(json.dumps({"recall": str(recall), "created": created}, ensure_ascii=False))


if __name__ == "__main__":
    main()
