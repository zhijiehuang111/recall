---
name: create-topic
description: 開新 Topic：一次一題訪談、用 Placement Quiz 測起點，寫出 Topic 計畫，並建立 Capstone Card 與它需要的前置卡。使用者說要開新 Topic、想學某個領域、不知道該學什麼時使用。
---

# create-topic：開新 Topic

只提議，使用者同意才寫入 `recall/`。不寫出題目的答案，作答前不透露 Rubric。

1. 照 `${CLAUDE_PLUGIN_ROOT}/references/vault-setup.md` 準備 Vault。`recall/topics/` 已有 2 個 `status: active` 的 Topic 時，先請使用者 pause 一個。
2. 使用者沒有想學的問題時，依 `recall/config.toml` 的 `target_roles` 與 `roadmap_sources` 挑幾個節點各問 1–2 題，把最弱的地方改寫成一個真的想知道答案的問題。
3. 訪談，一次一題：卡在哪、要交出什麼成果、一週有多少時間。
4. Placement Quiz 3–5 題，一次一題，照 `${CLAUDE_PLUGIN_ROOT}/references/grading.md` 評 Grade。
5. 寫 `recall/topics/<slug>.md`：frontmatter `status: active`，本文寫問題、目的地、順序、先不學什麼。
6. 照 `${CLAUDE_PLUGIN_ROOT}/references/card-writing.md` 逐張提議卡，全部帶 `topic: <slug>`：答好的題目原樣成卡，答不好的地方寫成新卡，再加恰好一張 `capstone: true` 的卡與它需要的前置卡。
7. 答好的題目寫入後記錄（答不好的不記）：

   ```bash
   uv run "${CLAUDE_PLUGIN_ROOT}/scripts/log.py" review <card> --grade <good|easy> --hints 0 --placement
   ```
