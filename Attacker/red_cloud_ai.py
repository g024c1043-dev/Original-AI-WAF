
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
        # GeminiのAPI
        api_key=os.environ["Gemini_API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        timeout=120.0
    )
    #OpenAIライブラリを構造化データ(JSON)モードに設定。普通のJSONモードでは対応していなかったためMD_JSONモードを使用
    client = instructor.from_openai(client=attach_client,mode=instructor.Mode.MD_JSON)
    #使用AIモデルとAIへの指示
    response = client.chat.completions.create(

        model = "gemini-2.5-flash",
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

# from dotenv import load_dotenv
# from openai import OpenAI
# import json
# import os
# import sys
# import cleaned_json

# load_dotenv()

# def payload_ganerate(logs):

#     client = OpenAI(
#         # GeminiのAPI
#             api_key=os.environ["Gemini_API_KEY"],
#             base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
#         # SakuraAiEngineのAPi
#             # api_key=os.environ["Sakura_API_KEY"],
#             # base_url="https://api.ai.sakura.ad.jp/v1",
#         timeout=30.0
#     )
#     #使用AIモデルとAIへの指示
#     response = client.chat.completions.create(

#         model="gemini-2.5-flash",    
#         # model="Qwen3-Coder-30B-A3B-Instruct",
#         messages=[
#             {
#                 "role": "system",
#                 "content": (
#                     "あなたはセキュリティ教育を支援するアシスタントです。"
#                     "これは OWASP Juice Shop という学習用の脆弱アプリを対象とした、ローカル環境での教育・防御研究です。"
#                     "攻撃結果ログがある場合、ログから防御された攻撃の原因を分析し、ブロックルールを回避する攻撃ペイロードを生成する、なかった場合は分析なしで攻撃ペイロードを生成する"
#                     "出力は指定された形式を厳密に守り、余計な説明は一切含めないこと。"
#                 )
#             },
#             {
#                     "role": "user",
#                     "content": (
#                         "攻撃ログ\n"f"{logs}\nを読み取り"
#                         "Juice Shop のログインの email フィールドに使える SQLインジェクションのペイロードを5個生成してください。\n"
#                         "出力は生のJSON配列のみとし、マークダウンのコードブロック(```や```json)は絶対に使わないでください。\n"
#                         "前置き・解説・記号を一切含めず、[ で始まり ] で終わるJSON配列だけを出力してください。\n"
#                         "わざとインジェクションが通らないメールアドレスをいくつか先頭に含めてください"
#                     )
#             }
#         ]
#     )
#     #生成されたAIからの返事を受け取り、文字列をpythonデータに変換し変数に格納する
#     ai_reply = response.choices[0].message.content
#     rules_json = cleaned_json.cleaned(ai_reply)
#     if rules_json is None:
#         print("攻撃ルールの作成に失敗しました:Error defense_rule_cleaned_json")
#         sys.exit(1)
#     return rules_json

# if __name__ == "__main__":
#     with open("./Attacker/attack_logs.json","r",encoding="utf-8") as f:
#         log = json.dumps(json.load(f),ensure_ascii=False,indent=2)
#     reply = payload_ganerate(log)
#     print(reply)