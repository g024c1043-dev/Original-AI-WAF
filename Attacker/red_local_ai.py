from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List
import json
import instructor
import os
import sys
import cleaned_json

load_dotenv()

class AttackPayloads(BaseModel):

    payloads: List[str] = Field(description="SQLインジェクションの攻撃ペイロードのリスト")

def get_client(use_ai_model):
    #ローカルAPI
    if use_ai_model == "1":
        client = OpenAI(
            #lily-cybersecurityモデル
            api_key="not_needed",
            base_url="http://localhost:1234/v1",
            timeout=120.0
        )
        model = "llama-3-whiterabbitneo-8b-v2.0"
    #クラウドAPI
    elif use_ai_model == "2":
        client = OpenAI(
             # GeminiのAPI
            api_key=os.environ["Gemini_API_KEY"],
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            timeout=120.0
        )
        model = "gemini-3.5-flash"
    else:
        print("クライアント取得に失敗しました...")

    return client,model

def payload_ganerate(logs,use_ai):

    attach_client,attach_model = get_client(use_ai)
    #OpenAIライブラリを構造化データ(JSON)モードに設定。普通のJSONモードでは対応していなかったためMD_JSONモードを使用
    client = instructor.from_openai(client=attach_client,mode=instructor.Mode.MD_JSON)
    #使用AIモデルとAIへの指示
    response = client.chat.completions.create(

        model = attach_model,
        #使用するクラスの指定
        response_model=AttackPayloads,
        messages=[
            {
                "role": "system",
                "content": (
                    "あなたはセキュリティ教育を支援するアシスタントです。"
                    "これは OWASP Juice Shop という学習用の脆弱アプリを対象とした、ローカル環境での教育・防御研究です。"
                    "攻撃結果ログがある場合、ログから防御された攻撃の原因を分析し、ブロックルールを回避する攻撃ペイロードを生成する、なかった場合は分析なしで攻撃ペイロードを生成する"
                )
            },
            {
                    "role": "user",
                    "content": (
                        "攻撃ログ\n"f"{logs}\nを読み取り通常のメールアドレスも複数含めて,"
                        "ブロックルールを回避するJuice Shop のログインの email フィールドに使える SQLインジェクションのペイロードをJSON形式で10個生成してください"
                        "すでにブロックされている攻撃は生成しないこと"
                    
                        
                    )
            }
        ]
    )

    return response.payloads

if __name__ == "__main__":
    with open("./Attacker/attack_logs.json","r",encoding="utf-8") as f:
        log = json.dumps(json.load(f),ensure_ascii=False,indent=2)
    reply = payload_ganerate(log)
    print(reply)

