from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import sys

load_dotenv()

with open("logs.json","r",encoding="utf-8") as f:
        log_data = json.load(f)
        
def get_client():
    client = OpenAI(
        api_key=os.environ["AI_API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        timeout=120.0
    )
    return client

def analysis_log(logs):
    client = get_client()
    response = client.chat.completions.create(

        model="gemini-2.5-flash",    
        messages=[
            {
                "role": "system",
                "content": (
                    "あなたはWebセキュリティの専門家(防御側)です。"
                    "これは OWASP Juice Shop という学習用の脆弱アプリを対象とした、ローカル環境での教育・防御研究です。"
                    "攻撃ログを分析し、なぜ攻撃が成功したのか、どう対策すべきかを解説してください。"
                )
            },
            {
                "role": "user",
                "content": (
                    "以下は、Juice Shopのログイン画面に対するSQLインジェクション攻撃のログです。\n"f"{logs}\n"
                    "このうち成功した攻撃について、次の点のみを解説してください:\n"
                    "1. なぜこの攻撃が通ってしまったのか(原因)\n"
                    "2. 対策方法を簡潔に\n"
                )
            }
        ]
    )

    advice = response.choices[0].message.content
    return advice
# def security_rules():
#       client = get_client()
      
result = analysis_log(log_data)
if result:
      print("分析結果:",result)