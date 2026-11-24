---
name: create-card
description: 建卡：從使用者指定的筆記或貼上的面試題提議一組 Card（附出處，Rubric 隱藏寫入），逐張經同意才寫入。使用者說要建卡、把筆記做成卡、把面試題加進 recall 時使用。
---

# create-card：建卡

你只提議卡片，寫入與否由使用者決定：除了第 1 步建立空的 `recall/` 骨架，使用者對某張卡明確說保留之前，不建立、不修改 `recall/` 裡的任何檔案。

所有指令都在使用者的 Vault 根目錄（目前工作目錄）執行。開始前先讀 `${CLAUDE_PLUGIN_ROOT}/references/card-writing.md`：範圍上限、Rubric 與出處要求、Card ID 規則、檔案格式都以它為準。

## 1. 準備 Vault

照 `${CLAUDE_PLUGIN_ROOT}/references/vault-setup.md` 做。

## 2. 讀素材

- **筆記**：讀使用者指定的檔案。找不到就問路徑，不要猜。
- **面試題**：使用者貼上的題目。先判斷範圍：一張卡考不完就說明為什麼太大，提議拆成哪幾張。

列出 `recall/cards/` 既有的卡，避免提議重複的概念或 Card ID。判斷重複可以讀既有卡的 Rubric，但告訴使用者時只說是哪張卡（Card ID 與 `title`）和新提議的哪張卡重疊，用新卡的題目描述重疊處，不說既有卡的 Rubric 要點。已有卡涵蓋同一個概念時告訴使用者；使用者想改那張卡而不是新增時，請使用者用 `edit-card`。

## 3. 提議一組卡

先給概覽，一張一行：Card ID、type、`title`。說明為什麼這樣切（尤其是拆分的理由），問使用者要不要增減。

卡片屬於某個 Topic 時才帶 `topic`：使用者提到某個 Topic，或素材明顯屬於 `recall/topics/` 裡的某個 Topic 時，提議帶上並讓使用者確認；不確定就省略。不建立 Capstone Card；使用者想要時，請使用者用 `create-topic`。

## 4. 逐張決定

一則訊息只處理一張卡。完整列出：

- Card ID、type、`title`、`topic`（有的話）
- 題目（Build Card 加驗收條件）
- 出處

Rubric 預設不顯示：照出處寫好，保留時直接存檔，不引用、不轉述、不暗示有幾點或涵蓋哪些面向。使用者看過 Rubric，第一次作答就不是自己想出來的。使用者明確要求看某張卡的 Rubric 時才給那張卡的，看完照樣處理。

然後停下來，請使用者選擇：

- **保留**：寫入 `recall/cards/<card-id>.md` 與 `recall/.rubrics/<card-id>.md`，告訴使用者寫入了哪兩個檔案，再處理下一張。寫入前再確認一次 `recall/cards/<card-id>.md` 不存在；已存在就提議新的 ID，使用者同意後才寫入。
- **修改**：照使用者的意思改完，Rubric 跟著題目重寫，重新列出這張卡，再問一次。改完若超出範圍上限，提議拆開。
- **丟棄**：不寫入任何檔案，處理下一張。

全部處理完後，一句話總結：寫入了哪些 Card ID、丟棄了幾張。
