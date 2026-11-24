# Recall

讓 agent 當教練而不是答案機的學習流程：決定學什麼、測程度、考你、聽你講、排間隔複習。學習紀錄存在你自己的 Vault（git 版控的筆記 repo）的 `recall/` 裡，與這組 skills 分開。

## 前提：安裝 uv

plugin 的腳本一律用 [uv](https://docs.astral.sh/uv/) 執行，uv 會自動取得需要的 Python 3.14，不必另外裝 Python。

## 安裝 plugin

這個 repo 本身就是 marketplace。在終端機執行：

```
claude plugin marketplace add zhijiehuang111/recall   # 正式：從 GitHub
claude plugin marketplace add ~/recall                 # 開發：本機 clone 的位置
claude plugin install recall@recall
```

## 使用

在 Vault 根目錄開 Claude Code，執行 `/recall:recall`。第一次執行會建立：

```
recall/
  config.toml     ← 每日分鐘數、Target Role、roadmap 來源
  cards/          ← 一張卡一個 <card-id>.md
  topics/
  .rubrics/       ← 每張卡的 Rubric，作答前不看
```

作答紀錄追加在 `recall/reviews.jsonl`。

要把筆記或面試題做成卡，執行 `/recall:create-card`：agent 提議一組卡、每張附出處，你逐張決定保留、修改或丟棄，同意的才寫入 `recall/`。Rubric 照出處寫好直接藏進 `.rubrics/`，預設不給你看，免得第一次作答變成背答案；想看某張卡的 Rubric 可以直接要求。

要修改既有卡，執行 `/recall:edit-card`：Card ID 不變，題目或 Rubric 大改時會問你要不要重置排程。
