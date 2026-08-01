from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List
import instructor
import json
import os
import sys
import cleaned_json

load_dotenv()

with open("./Defender/waf_logs.json","r",encoding="utf-8") as f:
        log_data = json.load(f)

class AttackPayloads(BaseModel):

    payloads: List[str] = Field(description="攻撃を防ぐためのブロックルールを生成")

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
    attach_client = get_client()
    client = instructor.from_openai(client=attach_client,mode=instructor.Mode.MD_JSON)
    response = client.chat.completions.create(

        model="lily-cybersecurity-7b-v0.2",
        response_model=AttackPayloads,
        messages=[
            {
                "role": "system",
                "content": (
                    "あなたはWebセキュリティの専門家(防御側)です。"
                    "これは OWASP Juice Shop という学習用の脆弱アプリを対象とした、ローカル環境での教育・防御研究です。"
                    "攻撃ログを分析し, 攻撃を防ぐためのブロックルールを生成してください。"
                 
                )
            },
            {
                "role": "user",
                "content": (
                    "攻撃ログ\n"f"{logs}\n"
                    "このログをもとに、攻撃を防ぐためのブロックルールを生成してください。"
                )
            }
        ]
    )

    return response.payloads
    # ai_reply = response.choices[0].message.content
    # rules_json = cleaned_json.cleaned(ai_reply)
    # if rules_json is None:
    #     print("防御ルールの生成に失敗しました:Error defense_rule_cleaned_json")
    #     sys.exit(1)
    # return rules_json
