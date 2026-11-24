# 寫 Card

`create-card`、`edit-card` 與 `create-topic` 共用。提議卡片、寫入卡片、修改卡片前都先讀這份。

## 範圍上限

一張卡只考一個概念。

| type | 用在 | 作答時間上限 |
|---|---|---|
| `recall` | 有明確正解、答案簡短 | 2–5 分鐘 |
| `explain` | 用自己的話講清楚因果或原理 | 2–5 分鐘 |
| `build` | 在空白目錄親手實作，以驗收條件檢查 | 30 分鐘內 |

出現下列任一情況就是太大，拆成多張：

- 答案要涵蓋兩個以上可以分開考的概念（「比較 A 與 B，並說明何時用哪個」→ A 是什麼、B 是什麼、怎麼選，各一張）。
- Rubric 要點超過 5 個才講得完。
- 預估作答時間超過上表上限。

拆出來的每張卡都要能單獨作答，題目不依賴另一張卡的內容。

## 每張卡必附

- **Rubric**：3–5 個要點，每點是答案必須涵蓋的一件事，寫成可以逐條對照的句子。
- **出處**：可查證的來源，卡片 frontmatter 的 `source` 與 Rubric 檔都要寫。
  - 從筆記建卡：出處是那篇筆記在 Vault 裡的相對路徑（例如 `notes/sql/group-by.md`）；只用到其中一段時，接 `#` 與原文的段落標題，照抄不改寫（例如 `notes/sql/group-by.md#HAVING`）。卡片與 Rubric 檔的出處寫法一致。Rubric 要點以筆記內容為準；筆記與你所知不一致時，先提出來問使用者，不要自行改成任何一方。
  - 從面試題或其他地方建卡：出處是能查證答案的資料，優先官方文件、規格、原始碼或書的章節。只寫這次對話裡實際讀過、或使用者提供的出處；查不到就說明並請使用者提供，不要憑記憶編網址。題目的來源（例如哪場面試）可以寫在本文，但不能取代出處。

## Card ID

- 英文 slug：小寫英文與數字，以單一個 `-` 連接，例如 `having-vs-where`；不用大寫、底線、空白或中文。
- 描述卡片考的概念，不帶日期或流水號。
- 建立後不可改：作答紀錄靠 Card ID 對應卡片。使用者想換說法時改 `title`。
- 不可與既有卡重複：`recall/cards/<card-id>.md` 已存在就換一個 ID。

## 檔案格式

### `recall/cards/<card-id>.md`

```markdown
---
title: HAVING 與 WHERE 的差別
type: recall
source: notes/sql/group-by.md
created: 2026-11-24
---

同一個查詢裡同時用 WHERE 與 HAVING 過濾，兩者分別在什麼時候生效？各舉一個只能用其中一個的條件。
```

- `type`、`created`、`topic`、`capstone` 必須是從行首寫起的單行 `key: value`，排程腳本只讀這幾行。
- `created` 是建卡當天日期（`date +%F`）。
- `topic` 只在卡片屬於某個 Topic 時寫，值是 `recall/topics/` 下的檔名（不含 `.md`）；獨立的卡（例如一題面試題）省略。
- `capstone: true` 由 `create-topic` 建 Capstone Card 時才寫，值只能是 `true`；其他卡省略這個欄位。
- `source` 有多個出處時可寫成 YAML 清單。
- 本文是題目，不寫答案、不寫 Rubric 要點、不暗示要點。

Build Card 的本文另加驗收條件。驗收條件是規格，作答前可以看；只寫要做到什麼、怎麼檢查，不寫做法：

```markdown
在空目錄實作一個 LRU cache：`get(key)` 與 `put(key, value)` 都是 O(1)，容量滿時淘汰最久沒用的項目。

## 驗收條件

- 容量 2：put 1、put 2、get 1、put 3 之後，get 2 回傳不存在
- 附自動化測試，一個指令就能跑完
```

### `recall/.rubrics/<card-id>.md`

```markdown
# having-vs-where

- WHERE 在分組前逐列過濾，不能用聚合函數
- HAVING 在 GROUP BY 之後過濾分組，可以用聚合函數
- 各舉出一個只能用其中一個的條件

## 出處

- notes/sql/group-by.md
```

Build Card 的 Rubric 檢查做法（用了什麼結構、為什麼滿足要求），不重複驗收條件；這樣寫死結果混過驗收也會被抓到。

## 大改與小改

修改既有卡時判斷屬於哪一種：

- **大改**：Rubric 要點增刪或意思改變、題目考的範圍變了、`type` 改了。舊的作答紀錄考的是另一題，會誤導排程，所以要問使用者是否寫入 reset。
- **小改**：錯字、措辭、`title`、補充或修正出處、驗收條件的寫法（要求不變）。不影響排程，不問 reset。
