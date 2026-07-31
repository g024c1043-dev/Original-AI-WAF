from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import sys
import cleaned_json

load_dotenv()

with open("./Defender/waf_logs.json","r",encoding="utf-8") as f:
        log_data = json.load(f)
        
def get_client():
    client = OpenAI(
        #lily-cybersecurityモデル
        api_key="not_needed",
        base_url="http://localhost:1234/v1",
        timeout=120.0
    )
    return client
      
def analysis_log(logs):
    client = get_client()
    response = client.chat.completions.create(

        model="lily-cybersecurity-7b-v0.2",
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
def generate_defense_rule(logs):
    client = get_client()
    response = client.chat.completions.create(

        # model="gemini-2.5-flash",    
        # model="Qwen3-Coder-30B-A3B-Instruct",
        model="llm-jp-3.1-8x13b-instruct4",
        messages=[
            {
                "role": "system",
                "content": (
                    "あなたはWebセキュリティの専門家(防御側)です。"
                    "これは OWASP Juice Shop という学習用の脆弱アプリを対象とした、ローカル環境での教育・防御研究です。"
                    "出力は指定された形式を厳密に守り,攻撃ログの分析から, 攻撃を防ぐためのブロックルールのみを生成してください。"
                    "不要な解説や説明は不要です,出力は指定形式のJSON配列のみとすること。"
                )
            },
            {
                "role": "user",
                "content": (
                    "以下は、Juice Shopのログイン画面に対するSQLインジェクション攻撃の分析ログです。\n"f"{logs}\n"
                    "この分析をもとに、攻撃を防ぐためのブロックルールを生成してください。"
                    "文字列パターンをJSON配列で出力してください。\n"
                    "各ブロックルールは、SQLインジェクションの文字列そのものを、 余計なクォートで囲まずに出力してください。"
                    "前置き・解説を一切含めず[ で始まるり]で終わる配列のみを出力。"
                )
            }
        ]
    )
    ai_reply = response.choices[0].message.content
    rules_json = cleaned_json.cleaned(ai_reply)
    if rules_json is None:
        print("防御ルールの生成に失敗しました:Error defense_rule_cleaned_json")
        sys.exit(1)
    return rules_json
