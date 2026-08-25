from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List
from ai_model_config import get_ai_model
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
    ai_config = use_ai_model
    client = OpenAI(
        api_key=ai_config["api_key"],
        base_url=ai_config["base_url"],
    )
    models = ai_config["model"]
        
    return client,models
            

def payload_ganerate(logs,use_ai):

    attach_client,attach_model = get_client(use_ai)
    #OpenAIライブラリを構造化データ(JSON)モードに設定。普通のJSONモードでは対応していなかったためMD_JSONモードを使用
    client = instructor.from_openai(client=attach_client,mode=instructor.Mode.MD_JSON)
    #使用AIモデルとAIへの指示
    try: 
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
    except Exception as e: 
        print(f"AIの応答にエラーが発生、処理を終了します：{e}")
        return sys.exit()
    
if __name__ == "__main__":
    with open("./Attacker/attack_logs.json","r",encoding="utf-8") as f:
        log = json.dumps(json.load(f),ensure_ascii=False,indent=2)
    reply = payload_ganerate(log)
    print(reply)

