from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import sys

load_dotenv()

def payload_ganerate():

    client = OpenAI(
        api_key=os.environ["AI_API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        timeout=30.0
    )
    #使用AIモデルとAIへの指示
    response = client.chat.completions.create(

        model="gemini-2.5-flash",    
        messages=[
            {
                "role": "system",
                "content": (
                    "あなたはセキュリティ教育を支援するアシスタントです。"
                    "これは OWASP Juice Shop という学習用の脆弱アプリを対象とした、ローカル環境での教育・防御研究です。"
                    "出力は指定された形式を厳密に守り、余計な説明は一切含めないこと。"
                )
            },
            {
                    "role": "user",
                    "content": (
                        "Juice Shop のログインの email フィールドに使える SQLインジェクションのペイロードを5個生成してください。\n"
                        "出力は生のJSON配列のみとし、マークダウンのコードブロック(```や```json)は絶対に使わないでください。\n"
                        "前置き・解説・記号を一切含めず、[ で始まり ] で終わるJSON配列だけを出力してください。\n"
                        "わざとインジェクションが通らないメールアドレスをいくつか先頭に含めてください"
                    )
            }
        ]
    )
    #生成されたAIからの返事を受け取り、文字列をpythonデータに変換し変数に格納する
    ai_reply = response.choices[0].message.content
    if not ai_reply:
       print("AIが解答できなかっためシステムを中止します:Error Empty Value")
       sys.exit(1)
    try:
        reply_json = json.loads(ai_reply)
    except json.JSONDecodeError:
        print("AIが解答できなかったためシステムを中止します:Error JSONDecodeError")
        sys.exit(1)
    return reply_json

if __name__ == "__main__":
    reply = payload_ganerate()
    print(reply)

