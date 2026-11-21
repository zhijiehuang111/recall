## 常用指令

```bash
uv run ruff check . && uv run ruff format --check .   # lint + 格式；自動修正用 `uv run ruff check --fix . && uv run ruff format .`
uvx pyright                                           # 型別檢查，跟 VS Code 的 Pylance 同引擎；範圍與 venv 設定在 pyproject.toml
uv run pytest                                         # 指令列測試
```

## 改東西時的約定

- **改 Python**：改完跑 ruff 和 pyright，兩個都要 0 error。這個 repo 沒有 CI，要自己跑。
- **Python 版本一律 3.14**：根目錄 `pyproject.toml` 與 `plugins/` 腳本的 PEP 723 都宣告 `>=3.14`；使用者端由 `uv run` 自動取得符合的 Python。

## Agent skills

### Issue tracker

Issue 放在 GitHub Issues（公開 repo），用 `gh` 操作；開之前先給使用者看草稿。See `docs/agents/issue-tracker.md`.

### Triage labels

用預設的 5 個 label：`needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`。See `docs/agents/triage-labels.md`.

### Domain docs

Single-context：根目錄一個 `GLOSSARY.md` + `docs/adr/`（用到才建）。See `docs/agents/domain.md`.
