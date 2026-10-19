"""新聞摘要小幫手：用 Gemini API 的「結構化輸出」把新聞整理成固定格式的 JSON。

執行：uv run main.py
輸入：data/news.json
輸出：site/results.json（作品頁會讀這個檔案）
"""

import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

# ---------- 設定 ----------
load_dotenv()  # 從 .env 讀取 GEMINI_API_KEY（.env 不會進 repo）
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
INPUT_FILE = Path("data/news.json")
OUTPUT_FILE = Path("site/results.json")
DELAY_SECONDS = 4  # 每篇之間稍等一下，避免超過免費額度的每分鐘上限


# ---------- 結構化輸出的格式（Pydantic schema） ----------
class NewsSummary(BaseModel):
    headline: str = Field(description="改寫後的精簡標題，20 字以內")
    summary: str = Field(description="新聞摘要，以繁體中文撰寫，80 字以內")
    key_points: list[str] = Field(description="3 個重點，每點 25 字以內")
    category: Literal["政治", "財經", "科技", "社會", "國際", "生活", "體育", "娛樂", "其他"]
    sentiment: Literal["正面", "中性", "負面"]
    keywords: list[str] = Field(description="3 到 5 個關鍵字")


PROMPT = """你是一位專業的新聞編輯。請閱讀以下新聞，依照指定的 JSON 格式整理。
規則：
1. 一律使用繁體中文。
2. 只能根據新聞內容，不可加入新聞沒有提到的資訊。
3. 情緒判斷以新聞事件本身對大眾的影響為準。

新聞標題：{title}
新聞內容：
{content}
"""


def summarize(client: genai.Client, article: dict) -> NewsSummary:
    response = client.models.generate_content(
        model=MODEL,
        contents=PROMPT.format(title=article["title"], content=article["content"]),
        config={
            "response_mime_type": "application/json",
            "response_schema": NewsSummary,  # 讓模型「一定」照這個格式回傳
        },
    )
    return response.parsed  # SDK 會自動轉成 NewsSummary 物件


def main() -> None:
    if not os.getenv("GEMINI_API_KEY"):
        raise SystemExit("找不到 GEMINI_API_KEY，請先建立 .env（可參考 .env.example）")

    client = genai.Client()  # 自動讀取環境變數 GEMINI_API_KEY
    articles = json.loads(INPUT_FILE.read_text(encoding="utf-8"))

    results = []
    for i, article in enumerate(articles, start=1):
        print(f"[{i}/{len(articles)}] 摘要中：{article['title']}")
        try:
            s = summarize(client, article)
            results.append({
                "original_title": article["title"],
                "source": article.get("source", ""),
                "url": article.get("url", ""),
                "original_length": len(article["content"]),
                **s.model_dump(),
            })
            print(f"   → {s.category}｜{s.sentiment}｜{s.headline}")
        except Exception as e:  # 單篇失敗不影響其他篇
            print(f"   ✗ 失敗：{e}")
        time.sleep(DELAY_SECONDS)

    taipei = timezone(timedelta(hours=8))
    output = {
        "model": MODEL,
        "generated_at": datetime.now(taipei).strftime("%Y-%m-%d %H:%M"),
        "count": len(results),
        "items": results,
    }
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n完成！共 {len(results)} 篇，已寫入 {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
