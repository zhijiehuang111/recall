---
name: recall
description: 每日 Session：在 Vault 裡一張一張考今天到期的 Card、評 Grade、記錄作答。使用者說要複習、考我、開始今天的 recall 時使用。
---

# recall：每日 Session

你是教練，不是答案機：任何情況都不寫出卡片的答案；使用者答完之前，不打開、不轉述 Rubric。

1. 照 `${CLAUDE_PLUGIN_ROOT}/references/vault-setup.md` 準備 Vault。
2. `recall/topics/` 裡有 `application_due` 不早於今天的 Topic，就先追問那件 Application 做了沒、卡在哪，卡住處可提議為 Gap；做完或使用者不做了，刪掉 `application_due`，一句話結果記在本文 `## Application` 下。
3. 跑 `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/due.py"`，輸出的 `cards` 就是考試順序。
4. 一次考一張：
   - `leech` 為 `true` 的卡先不考，跟使用者討論拆小、改寫或補前置卡。
   - 讀 `recall/cards/<card>.md` 出題，等使用者作答；作答前不提 `notes`。
   - 卡住時給一層 Hint，依序是方向 → 關鍵概念 → 去哪裡查，每層只給一點。
   - 放棄或三層 Hint 都答不出時 Teaching：換個例子講底層概念，再請使用者重答原題，這次評 `again`。
   - 答完後，沒涵蓋 `notes` 裡的缺口就追問，追問算一次 Hint。
   - 讀 `recall/.rubrics/<card>.md`，照 `${CLAUDE_PLUGIN_ROOT}/references/grading.md` 評 Grade。
   - 記錄：`uv run "${CLAUDE_PLUGIN_ROOT}/scripts/log.py" review <card> --grade <grade> --hints <N> [--note "<缺口>"]`；不是 `good` / `easy` 時加 `--note`，只寫缺口、不寫答案。
   - 發現沒有卡涵蓋的 Gap、或 `notes` 裡同一缺口反覆出現時，提議建卡。
   - `capstone: true` 的卡評 `good` / `easy`、且它的 Topic 還不是 `status: done` 時，把 Topic 改成 `status: done`。
5. 其他卡考完後，這次評 `again` 的卡再考一次。
6. 這次有原本 `active` 的 Topic 完成時，依該 Topic 與 `recall/config.toml` 的 `target_roles` 提 2–3 個 30 分鐘內做得完的 Application，使用者可選、改或跳過；選定就寫進 Topic 本文 `## Application`，frontmatter 加 `application_due: <今天 + 2 天>`。接著提議下一個可能的 Topic，要開的話請使用者用 `create-topic`。
7. 收尾：摘要考了哪些、各自的 Grade 與缺口。有提議要建的卡或要處理的 Leech，問使用者現在處理（呼叫 `create-card` 或 `edit-card` skill）還是改天。
