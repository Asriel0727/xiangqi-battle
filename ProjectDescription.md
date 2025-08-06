# GitAction 象棋遊戲 (Xiangqi Battle)

一個透過 GitHub Actions 與 GitHub Issues 操控的中國象棋對戰系統，結合 Python 腳本，自動進行合法走法判定、棋譜記錄與棋盤圖像更新。

## 🎮 功能特色

-  透過 **GitHub Issue** 控制對局流程
-  支援合法移動判斷與完整象棋規則
-  自動產生棋盤圖並更新至專案頁面
-  自動更新 `README` 呈現當前棋局狀態
-  對局結束後自動判斷勝負與記錄歷史

## 🛠️ 技術架構

| 技術 | 說明 |
|------|------|
| GitHub Actions | 自動觸發處理棋步與狀態更新 |
| GitHub Issues | 作為玩家互動介面與指令輸入點 |
| Python | 執行象棋規則判定、棋盤狀態更新 |
| Pillow | 棋盤圖像生成 |
| Markdown | 棋譜與棋盤狀態顯示 |


## 📁 專案結構
```
├── .github/workflows/  
│ └── xiangqi.yml
│ └── readme_translate.yml
├── data/
│ └── board.json
├── images/  
│ └── board/
│ └── pieces/
│ └── board.png
├── scripts/
│ └── readme_updater.py
│ └── requirements.txt
│ └── xiangqi.py
│ └── xiangqi_rules.py
├── .gitignore
├── README.en.md
├── README.md
```
