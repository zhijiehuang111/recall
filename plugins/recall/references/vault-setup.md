# 準備 Vault

`recall`、`create-card`、`create-topic` 開始時都先做這一步。在使用者的 Vault 根目錄（目前工作目錄）執行：

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/init.py"
```

這一步確保 Vault 裡有 `recall/`；已經有了就什麼都不改。

輸出是 `"created": true`，代表這是使用者第一次在這個 Vault 用 recall。用一句話告訴使用者：剛建立了 `recall/`、每日分鐘數等設定在 `recall/config.toml`。輸出是 `"created": false` 就不提，直接往下。

指令回報 `uv: command not found` 時，請使用者照 <https://docs.astral.sh/uv/> 安裝 uv，然後結束，不進行後面的步驟。
