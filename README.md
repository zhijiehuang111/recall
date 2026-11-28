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

要開新 Topic，執行 `/recall:create-topic`：agent 一次問一題了解你的狀況、出 3–5 題 Placement Quiz 測起點，寫出 Topic 計畫，再提議 Capstone Card 與前置卡。答得好的題目直接成卡、從較長的間隔起算；沒有想學的問題時，agent 依 `config.toml` 的 Target Role 與 roadmap 幫你找弱點。同時最多 2 個 active Topic。Capstone Card 要等同 Topic 其他卡都答對過才開考，通過即 Topic 完成，agent 會列 2–3 個 Application 候選（把學到的用在真實情境的小事，30 分鐘做得完），你挑一個、改一下或跳過；選了就在 48 小時內做完，下次 Session 開場會問你做了沒。Topic 設為 paused 或 done 時，考過的卡照常複習，沒考過的先不出現。

要修改既有卡，執行 `/recall:edit-card`：Card ID 不變，題目或 Rubric 大改時會問你要不要重置排程。
