# Recall 設計摘要

整理自設計訪談（2026-11-20）。名詞定義見 [GLOSSARY.md](../GLOSSARY.md)，學習方法依據 `video.txt` 的五步：決定學什麼 → 查起點 → 考我 → 講給它聽 → 間隔複習 + 48 小時內用出來。

## 核心原則

- agent 是教練不是答案機：只給 Hint；不會時進入 Teaching（換例子講底層概念），之後使用者必須自己重答原題。任何情況都不寫出該卡答案。
- 使用者作答前，agent 不引用或轉述 Rubric。
- agent 只「提議」卡片與 Topic，使用者同意才寫入。
- 程度一律用測驗判斷，不採自我評估。

## 架構

- 本 repo 是 Claude Code plugin（skills + 腳本），與學習紀錄分離。
- 使用者在自己的 Vault（git 版控的筆記 repo）中執行 Claude Code；Vault 內有 `recall/` 即代表啟用。
- 腳本一律 `uv run` 執行，v1 不加第三方套件。

```
recall/
  config.toml              ← 每日時間預算、Target Role、roadmap 來源
  topics/<topic>.md        ← 目的地、先不學什麼、Milestone、Application、狀態
  cards/<card-id>.md       ← 題目、type、topic、出處
  .rubrics/<card-id>.md    ← Rubric（點開頭資料夾，避免作答前看到）
  workspace/<card-id>/     ← Build Card 的練習目錄，每次複習從空目錄重做
  reviews.jsonl            ← 作答／reset 事件，只追加
```

- 排程狀態不落地，由 `reviews.jsonl` 重播算出（[ADR 0001](adr/0001-schedule-derived-from-review-log.md)）。
- Card ID 為英文 slug，建立後不可改。
- 「今天」以本地時間午夜換日。

## 排程與評分

- 演算法：簡化 SM-2，可替換。
- agent 依作答過程評 Grade，需說明理由，使用者可推翻：

| Grade | 條件 |
|---|---|
| Again（= Lapse） | 進入 Teaching，或被指出錯誤後仍補不起來 |
| Hard | 用了 Hint 才答出，或漏了要點 |
| Good | 沒用 Hint，Rubric 要點都有 |
| Easy | 沒用 Hint、完整，且有正確延伸 |

- 同一 Session 內 Lapse 的卡最後再考一次；下一 Session 先考 Lapse / Hard 的卡。
- 作答暴露出的 Gap，經同意後建新卡。
- Lapse 累積 3 次 → Leech：停下來討論拆小、改寫或補前置卡。
- 卡片大改（Rubric 要點或範圍變了）→ 詢問是否寫入 `reset` 事件；小改不影響排程。
- 每日份量依時間預算：到期複習優先，剩餘預算才加新卡。

## 範圍上限

- Recall / Explain Card：一個概念，2–5 分鐘。
- Build Card：30 分鐘內。
- Topic：一到兩週內可達第一個 Milestone，同時最多 2 個 active。
- Application：30 分鐘內、48 小時內完成，可跳過，不進排程。

## 卡片類型

- **Recall**：明確正解、短答。
- **Explain**：用自己的話講因果／原理，agent 只指出模糊、錯誤、遺漏，不改寫。
- **Build**：空目錄實作，附驗收條件（規格，可先看）；評分 = 驗收通過 + 依 Rubric 檢查做法。

## 流程（skills）

- **`recall`**：每日 Session。先追問上次 Application，再考到期卡，最後加新卡。Hint、Teaching、評分、Gap 都在此處理。
- **`recall-topic`**：開新 Topic。訪談（一次一題）→ 程度測驗（3–5 題，答好的直接成卡並記 Good）→ 計畫（目的地、順序、先不學什麼、Milestone）→ 只建第一個 Milestone 需要的卡。agent 自行出題時，以 roadmap（預設 roadmap.sh Backend / Full Stack / AI Engineer，可加 JD 或題庫）當地圖：依 Target Role 挑節點快速測驗找弱點，再把弱點改寫成「真的想知道答案的問題」。
- **`recall-card`**：從筆記或面試題提議卡片；面試題太大就拆。
- 首次執行時若無 `recall/`，自動建立並產生預設 `config.toml`。
- 腳本：`due.py`（依時間預算列今日卡）、`log.py`（寫入一筆事件）。
- Hint / Teaching / 評分等規則以參考檔拆分，不拆成獨立 skill；「教練鐵則」寫在 `recall` 主檔，評分規則放在 plugin 共用位置，`recall` 與 `recall-topic` 共用。

## Topic 狀態

`active` / `paused` / `done`（最後一個 Milestone 通過即 done）。Card 的複習不受 Topic 狀態影響；非 active 時不再新增卡、不提議 Application。

## 延後／待考慮

- **Mock Interview Session**：agent 扮面試官出開放題並追問，回饋產生 Gap；不計入單卡排程。有需要再做。
- **評分 subagent**：教練不讀 Rubric，作答後交給獨立評分 subagent 給 Grade，換取更嚴格且杜絕 Rubric 洩漏，代價是延遲與 Hint 精準度。若實際使用發現評分太寬鬆或洩漏答案再採用，屆時寫 ADR。
- **卡片依 Target Role 標籤篩選**：v1 不做。
- **FSRS**：演算法介面預留，之後替換。
