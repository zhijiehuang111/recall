# 排程狀態由作答紀錄重算，不存在 Card 裡

每次作答只在 `recall/reviews.jsonl` 追加一行事件（作答、reset）；下次考試日、間隔、難度等排程狀態從不落地，每次由腳本從頭重播這份紀錄、套用排程演算法算出。我們沒有把 `due`／`interval` 寫進 Card 的 frontmatter，因為那會讓同一件事有兩份資料而可能不一致，且日後換演算法（SM-2 → FSRS）只需用新演算法重播同一份紀錄，不必遷移資料；Card 檔也因此只在內容被改時才變動。

## Consequences

- `reviews.jsonl` 是唯一真相來源，只能追加、不能改寫既有行；要「重來」就寫一筆 `reset` 事件。
- Card ID 建立後不可改名，因為紀錄以 ID 對應卡片。
