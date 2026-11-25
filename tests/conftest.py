"""指令列測試的共用工具：在暫存目錄建假 Vault，用 `uv run` 跑 plugin 腳本。

測試只看 stdout 的 JSON、結束狀態與腳本寫進 Vault 的檔案，不 import 腳本內部。
"""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "plugins" / "recall" / "scripts"


@dataclass
class Result:
    code: int
    stdout: str
    stderr: str

    def json(self):
        return json.loads(self.stdout)


def run_script(name: str, *args: str, cwd: Path) -> Result:
    proc = subprocess.run(
        ["uv", "run", "--quiet", str(SCRIPTS / f"{name}.py"), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,  # 測試要自己斷言 exit code
    )
    return Result(proc.returncode, proc.stdout, proc.stderr)


class Vault:
    def __init__(self, root: Path):
        self.root = root
        self.recall = root / "recall"

    def init(self) -> Vault:
        (self.recall / "cards").mkdir(parents=True, exist_ok=True)
        self.set_daily_minutes(30)
        return self

    def set_daily_minutes(self, minutes: int) -> None:
        (self.recall / "config.toml").write_text(f"daily_minutes = {minutes}\n")

    def add_card(
        self,
        card_id: str,
        *,
        type: str = "recall",
        created: str = "2026-11-01",
        extra: str = "",
    ) -> None:
        frontmatter = (
            f"---\ntitle: {card_id}\ntype: {type}\ncreated: {created}\n{extra}---\n"
        )
        (self.recall / "cards" / f"{card_id}.md").write_text(frontmatter + "\n題目\n")

    def write_card(self, card_id: str, text: str) -> None:
        (self.recall / "cards" / f"{card_id}.md").write_text(text)

    @property
    def log_path(self) -> Path:
        return self.recall / "reviews.jsonl"

    def log_lines(self) -> list[str]:
        if not self.log_path.exists():
            return []
        return self.log_path.read_text().splitlines()

    def due(self, *args: str, cwd: Path | None = None) -> Result:
        return run_script("due", *args, cwd=cwd or self.root)

    def log(self, *args: str, cwd: Path | None = None) -> Result:
        return run_script("log", *args, cwd=cwd or self.root)

    def review(self, card_id: str, grade: str, at: str, *, hints: int = 0) -> Result:
        return self.log(
            "review", card_id, "--grade", grade, "--hints", str(hints), "--at", at
        )

    def reset(self, card_id: str, at: str) -> Result:
        return self.log("reset", card_id, "--at", at)

    def init_script(self, *args: str, cwd: Path | None = None) -> Result:
        return run_script("init", *args, cwd=cwd or self.root)


@pytest.fixture
def vault(tmp_path: Path) -> Vault:
    return Vault(tmp_path / "vault")


@pytest.fixture
def ready_vault(vault: Vault) -> Vault:
    vault.root.mkdir()
    return vault.init()
