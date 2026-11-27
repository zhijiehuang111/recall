---
name: edit-card
description: 改卡：修改既有 Card 的題目、title、出處或 Rubric；Card ID 不變，大改時詢問是否重置排程。使用者說要改某張卡、修正卡片、改 Rubric 時使用。
---

# edit-card：改卡

列出改後的內容，使用者同意才寫入。卡片怎麼寫、大改與小改照 `${CLAUDE_PLUGIN_ROOT}/references/card-writing.md`。

1. 找到 `recall/cards/<card-id>.md`；使用者沒給 Card ID 就列出可能的卡請使用者指定。
2. 讀卡片與 `recall/.rubrics/<card-id>.md`，照使用者的意思改；不顯示 Rubric，除非使用者要改它或明確要求看。檔名不改。
3. 改完超出範圍上限，提議拆開，多出的部分請使用者用 `create-card` 建。
4. 大改時問使用者要不要重置排程（重置後當新卡重新起算），同意才跑 `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/log.py" reset <card-id>`。
