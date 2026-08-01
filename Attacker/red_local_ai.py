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

def payload_ganerate(logs):
    #LM Stdudioと接続
    attach_client = OpenAI(
        # LM StudioのAPI
            api_key="not_needed",
            base_url="http://localhost:1234/v1",
        timeout=30.0
    )
    #OpenAIライブラリを構造化データ(JSON)モードに設定。普通のJSONモードでは対応していなかったためMD_JSONモードを使用
    client = instructor.from_openai(client=attach_client,mode=instructor.Mode.MD_JSON)
    #使用AIモデルとAIへの指示
    response = client.chat.completions.create(

        model = "llama-3-whiterabbitneo-8b-v2.0",
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
                        "攻撃ログ\n"f"{logs}\nwを読み取り"
                        "Juice Shop のログインの email フィールドに使える SQLインジェクションのペイロードをJSON形式で5個生成してください。\n"
                        
                    )
            }
        ]
    )

    return response.payloads
    
    # if not ai_reply:
    #     print("AIが解答できなかっためシステムを中止します:Error Empty Value")
    #     sys.exit(1)
    # try:
    #      reply_json = json.loads(ai_reply)
    # except json.JSONDecodeError:
    #     print("AIが解答できなかったためシステムを中止します:Error JSONDecodeError")
    #     sys.exit(1)
    # return reply_json
    # return ai_reply

if __name__ == "__main__":
    with open("./Attacker/attack_logs.json","r",encoding="utf-8") as f:
        log = json.dumps(json.load(f),ensure_ascii=False,indent=2)
    reply = payload_ganerate(log)
    print(reply)

