---
name: create-card
description: 建卡：從使用者指定的筆記或貼上的面試題提議一組 Card（附出處，Rubric 隱藏寫入），逐張經同意才寫入。使用者說要建卡、把筆記做成卡、把面試題加進 recall 時使用。
---

# create-card：建卡

只提議，使用者說保留才寫入 `recall/`。卡片怎麼寫照 `${CLAUDE_PLUGIN_ROOT}/references/card-writing.md`。

1. 照 `${CLAUDE_PLUGIN_ROOT}/references/vault-setup.md` 準備 Vault。
2. 讀使用者指定的筆記或貼上的面試題；一張卡考不完就提議怎麼拆。
3. 對照 `recall/cards/` 既有的卡，重複的告訴使用者是哪張（不說它的 Rubric），想改那張就請使用者用 `edit-card`。
4. 先一張一行列出概覽：Card ID、type、`title`。素材明顯屬於某個 `status: active` 的 Topic 才提議帶 `topic`；不建 Capstone Card，要的話請使用者用 `create-topic`。
5. 一次一張列出題目（Build 加驗收條件）與出處，不給看 Rubric（使用者明確要求才給），請使用者選保留、修改或丟棄。
