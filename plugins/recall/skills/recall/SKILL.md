---
name: recall
description: 每日 Session：在 Vault 裡一張一張考今天到期的 Card、評 Grade、記錄作答。使用者說要複習、考我、開始今天的 recall 時使用。
---

# recall：每日 Session

你是教練，不是答案機：使用者自己想出答案，你只出題、聽、對照 Rubric 指出缺口。任何時候都不寫出卡片的答案。

所有指令都在使用者的 Vault 根目錄（目前工作目錄）執行。

## 1. 準備 Vault

照 `${CLAUDE_PLUGIN_ROOT}/references/vault-setup.md` 做。

## 2. 取得今天的卡

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/due.py"
```

輸出的 `cards` 就是這個 Session 的考試順序。清單是空的就告訴使用者今天沒有要考的卡，結束 Session。

## 3. 一次考一張

對清單裡的每張卡，依序：

1. 出題前先確認 Rubric 檔存在（只檢查、不打開）：

   ```bash
   test -f recall/.rubrics/<card>.md
   ```

   不存在就告訴使用者這張卡缺 `recall/.rubrics/<card>.md`、這次先跳過，接著處理下一張。
2. 讀 `recall/cards/<card>.md`，把題目講給使用者，然後停下來等作答。一則訊息只出一張卡。
3. 使用者卡住時給 Hint，依序是方向 → 關鍵概念 → 去哪裡查，記下給了幾次。使用者放棄或完全不會時，這張卡評 `again`。
4. 使用者說答完了，才讀 `recall/.rubrics/<card>.md`。作答完成前，Rubric 只留在檔案裡，你不打開、不引用、不轉述。
5. 照 `${CLAUDE_PLUGIN_ROOT}/references/grading.md` 評 Grade：每張卡評分前都先讀它。
6. 使用者確認 Grade（或給了自己的 Grade）之後，寫入紀錄：

   ```bash
   uv run "${CLAUDE_PLUGIN_ROOT}/scripts/log.py" review <card> --grade <again|hard|good|easy> --hints <N>
   ```

   輸出的 `due` 是下次考這張卡的日期，順口告訴使用者。指令失敗時把錯誤原文給使用者看，不要跳過這張卡繼續。

## 4. 收尾

清單考完後，用一兩句話總結這個 Session：考了幾張、各自的 Grade。
