# 新聞摘要小幫手 News Summarizer

用 Python 呼叫 Google Gemini API，透過 **結構化輸出（Structured Output）** 將新聞整理成固定格式的 JSON（標題、摘要、重點、分類、情緒、關鍵字），並用 GitHub Actions 自動部署作品頁到 GitHub Pages。

- 作品頁：https://<你的帳號>.github.io/<repo 名稱>/
- 使用的 LLM 能力：結構化輸出（Pydantic schema → JSON）

## 功能

| 欄位 | 說明 |
|---|---|
| `headline` | 改寫後的精簡標題（20 字內） |
| `summary` | 繁體中文摘要（80 字內） |
| `key_points` | 3 個重點 |
| `category` | 政治／財經／科技／社會／國際／生活／體育／娛樂／其他 |
| `sentiment` | 正面／中性／負面 |
| `keywords` | 3–5 個關鍵字 |

## 專案結構

```
.
├── .github/workflows/deploy.yml  # 自動部署 GitHub Pages
├── data/news.json                # 輸入：要摘要的新聞
├── site/
│   ├── index.html                # 作品頁
│   └── results.json              # 輸出：程式產生的摘要結果
├── main.py                       # 主程式
├── pyproject.toml                # uv 套件設定
├── .env.example                  # 金鑰範例（不含真實金鑰）
└── .gitignore                    # 排除 .env
```

## 執行步驟

1. 到 [Google AI Studio](https://aistudio.google.com/) 取得免費 API key
2. 安裝套件：
   ```bash
   pip install uv   # 若尚未安裝 uv
   uv sync
   ```
3. 建立 `.env` 並填入金鑰：
   ```bash
   cp .env.example .env
   ```
4. 執行：
   ```bash
   uv run main.py
   ```
5. 將 `site/results.json` commit 並 push，GitHub Actions 會自動部署作品頁。

## 更換新聞

編輯 `data/news.json`，每篇格式如下：

```json
{ "title": "新聞標題", "source": "來源媒體", "url": "原文網址", "content": "新聞全文" }
```

## 安全性

API 金鑰只放在 `.env`，該檔已列入 `.gitignore`，不會進入 repo 或 commit 歷史。

## AI 使用說明

（請依實際情況填寫：用了哪些 AI 工具、用在哪裡、自己修改或驗證了什麼）
