---
name: edit-card
description: 改卡：修改既有 Card 的題目、title、出處或 Rubric；Card ID 不變，大改時詢問是否重置排程。使用者說要改某張卡、修正卡片、改 Rubric 時使用。
---

# edit-card：改卡

改什麼由使用者決定：列出改後的內容、使用者明確同意之前，不修改 `recall/` 裡的任何檔案。

所有指令都在使用者的 Vault 根目錄（目前工作目錄）執行。開始前先讀 `${CLAUDE_PLUGIN_ROOT}/references/card-writing.md`：範圍上限、Rubric 與出處要求、Card ID 規則、檔案格式、大改與小改都以它為準。

## 1. 找到卡

使用者給了 Card ID 就讀 `recall/cards/<card-id>.md`。只描述了卡的內容、或檔案不存在時，列出 `recall/cards/` 裡可能的卡請使用者指定，不要猜。找不到 `recall/` 就告訴使用者這個 Vault 還沒有卡，結束。

## 2. 改內容

1. 讀 `recall/cards/<card-id>.md` 與 `recall/.rubrics/<card-id>.md`，跟使用者確認要改什麼。
2. 列出改後的內容，使用者同意才寫入。改完若超出範圍上限，提議拆成多張：原卡留下其中一部分，其餘的請使用者用 `create-card` 建。縮小範圍時，被拿掉的部分使用者若還想考，也請使用者用 `create-card` 建。
3. Rubric 預設不顯示：使用者要改 Rubric、或明確要求看時才列出。題目改了而 Rubric 也得跟著改時，告訴使用者 Rubric 會一起更新，不列內容。
4. 依 `card-writing.md` 的 Card ID 規則，檔案不改名、不搬移。

## 3. 判斷是否重置排程

依 `card-writing.md` 的「大改與小改」判斷：

- **小改**：直接寫入，不提排程。
- **大改**：寫入後問使用者是否重置排程，說明重置後這張卡會當作新卡重新起算、舊紀錄保留但不再計入。使用者同意才執行：

  ```bash
  uv run "${CLAUDE_PLUGIN_ROOT}/scripts/log.py" reset <card-id>
  ```

  指令失敗時把錯誤原文給使用者看。
