# Recall

一套讓 agent 當「教練」而不是「答案機」的學習流程：決定學什麼、測程度、考你、聽你講、排間隔複習。學習紀錄存在使用者自己的 Vault 裡，與這組 skills 分開。

## Language

### 場域

**Vault**:
使用者自己的筆記 repo（自行用 git 版控），學習紀錄存放於其中；使用者在 Vault 裡執行 agent 來使用這組 skills。
_Avoid_: workspace, 筆記庫, project

### 學習內容

**Topic**:
一個使用者真的想知道答案的問題（例如「為什麼高併發時庫存會被扣成負數？」），帶有目的地與先不學什麼；約一到兩週可完成，Capstone Card 通過即結束。範圍變大時拆成下一個 Topic，而非分階段。
_Avoid_: 主題, subject, 課程, 題目

**Capstone Card**:
證明使用者已抵達 Topic 目的地的那張收尾 Card（通常是 Build 或 Explain），每個 Topic 恰有一張；同 Topic 其他卡都至少答對過一次才開考，首次評為 Good / Easy 即代表 Topic 完成。
_Avoid_: Milestone, 里程碑, 期末考, final

**Application**:
Topic 完成後，把學到的東西用在真實情境（side project、短文、面試式回答）的一件小事；由 agent 提出候選、使用者選定，30 分鐘內、48 小時內完成，可跳過，不進排程。
_Avoid_: 作業, homework, project

**Target Role**:
使用者正在準備的職缺方向（例如 backend、full-stack、AI 應用），用來挑選 Topic。
_Avoid_: 職位, track, career path

**Card**:
排程的最小單位，只考一個概念；可屬於某個 Topic，也可獨立存在（例如一題面試題）。
_Avoid_: 題目, question, flashcard, item

**Recall Card**:
有明確正解、答案簡短的 Card，對照 Rubric 判斷對錯。
_Avoid_: 問答題, 選擇題

**Explain Card**:
要求使用者用自己的話講清楚因果或原理的開放式 Card，對照出處找出模糊、錯誤、遺漏處，不代為改寫。
_Avoid_: 申論題, 費曼卡

**Build Card**:
要求使用者在空白練習目錄中親手實作、並以驗收條件檢查的 Card；每次複習都從零重做。
_Avoid_: 實作題, exercise, project

### 引導

**Hint**:
agent 在使用者卡住時給的線索，依序為：方向 → 關鍵概念 → 去哪裡查；永遠不包含該題答案本身。
_Avoid_: 提示詞, clue, 解答

**Teaching**:
使用者放棄或完全不會時，agent 改用另一個例子或指向參考資料講解底層概念；結束後使用者必須自己重新作答原題。
_Avoid_: 解題, 示範答案, walkthrough

### 考核

**Rubric**:
一張卡的評分重點：3–5 個答案必須涵蓋的要點，附可查證的出處；使用者作答完成前不應看到。
_Avoid_: 答案, answer key, 標準答案

**Placement Quiz**:
開新 Topic 時用來判斷起點的 3–5 題測驗；答得好的題目直接成為 Card，並從較長的間隔開始；答不好的地方寫成新卡。
_Avoid_: 程度測驗, pretest, diagnostic

**Session**:
一輪連續的複習，從到期最久與上次出錯的卡開始考起。
_Avoid_: 練習, round, 一回

**Gap**:
作答時暴露出、但目前沒有任何卡涵蓋的知識缺口；經使用者同意後會變成新卡。
_Avoid_: 盲點, weakness

**Grade**:
agent 依作答過程給一次作答的評分，共四級：Again、Hard、Good、Easy；使用者可推翻。
_Avoid_: 分數, score, rating

**Lapse**:
被評為 Again 的一次作答（需要 Teaching，或答錯後補不起來），會讓該卡很快再出現。Lapse 是事件，不是第五種 Grade。
_Avoid_: 失敗, fail, wrong

**Leech**:
累積 Lapse 達 3 次的 Card，代表卡片本身可能太大、問法模糊或缺前置知識，需要重新檢視而非繼續考。
_Avoid_: 難題, 卡關題
