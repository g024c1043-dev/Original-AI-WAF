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

class Block_Scoring_Rule(BaseModel):

    id: str = Field(description="変更対象のルールID")
    score: int = Field(description="変更後のスコア")    
    
class ScoringRules(BaseModel):

    rules: List[Block_Scoring_Rule] = Field(description="既存の防御ルールに対する変更後のスコア一覧")

class DefenseRule(BaseModel):

    id: str = Field(description="ルールID")
    pattern: str = Field(description="ルールのパターン")
    score: int = Field(description="ルールのスコア")
    name: str = Field(description="ルールの名前")

class Generate_Defense_Rules(BaseModel):

    rules: List[DefenseRule] = Field(description="既存のルールへのルール追加後のスコア一覧")

def get_client():
    client = OpenAI(
       # GeminiのAPI
        api_key=os.environ["Gemini_API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        timeout=120.0
    )
    return client

#解説用AI関数
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
#防御ルール生成用AI関数
def generate_defense_rule(logs,rules):
    attach_client = get_client()
    client = instructor.from_openai(client=attach_client,mode=instructor.Mode.MD_JSON)
    response = client.chat.completions.create(

        model="gemini-2.5-flash",
        response_model=Generate_Defense_Rules,
        messages=[
            {
                "role": "system",
                "content": (
                    "あなたはWebセキュリティの専門家(防御側)です。"
                    "これは OWASP Juice Shop という学習用の脆弱アプリを対象とした、ローカル環境での教育・防御研究です。"
                    "攻撃ログを読み取った結果から、欠如している防御ルールを生成する、なおすでに存在するルールは生成しないこと"
                 
                )
            },
            {
                "role": "user",
                "content": (
                    "攻撃ログ\n"f"{logs}\n"
                    "攻撃ログの結果から、"f"{rules}内のルールと同じ形式で、欠如している防御ルールを生成"
                    "現在のWAFはスコア合計40以下は許可、40~80は警告、80以上はブロックする仕様である"
                )
            }
        ]   
    )
    
    return response.rules
#防御ルールスコアリング調整用AI関数
def scoring_defense_rule(logs,rules):
    attach_client = get_client()
    client = instructor.from_openai(client=attach_client,mode=instructor.Mode.MD_JSON)
    response = client.chat.completions.create(

        model="gemini-2.5-flash",
        response_model=ScoringRules,
        messages=[
            {
                "role": "system",
                "content": (
                    "あなたはWebセキュリティの専門家(防御側)です。"
                    "これは OWASP Juice Shop という学習用の脆弱アプリを対象とした、ローカル環境での教育・防御研究です。"
                    "攻撃ログを読み取った結果から必要に応じたスコアの調整を実施すること。"
                 
                )
            },
            {
                "role": "user",
                "content": (
                    "攻撃ログ\n"f"{logs}\n"
                    "攻撃ログの結果から、"f"{rules}内にあるルールの危険と判断した攻撃に対するルールのスコアを高く、スコアが高すぎるルールのスコアを低くするスコア調整を実施"
                    "現在のWAFはスコア合計40以下は許可、40~80は警告、80以上はブロックする仕様である。"
                )
            }
        ]   
    )
    
    return response.rules

def update_rule(rules,scoring_rules):

    #生成したルール分の辞書を作成
    update_rules = {
        #idはキー、値はscoreの数値のみ
        i.id: i.score
        for i in scoring_rules
    }
    print("スコアリング調整後のルール:",update_rules)

    #wafのスコアリングルール分ループ
    for i in rules:
        #生成したルールが既存のルールに存在する場合、スコアを更新
        if i.id in update_rules:
            i.score = update_rules[i.id]

    return rules
  
# from dotenv import load_dotenv
# from openai import OpenAI
# import json
# import os
# import sys
# import cleaned_json

# load_dotenv()

# with open("./Defender/waf_logs.json","r",encoding="utf-8") as f:
#         log_data = json.load(f)
        
# def get_client():
#     client = OpenAI(
#         # GeminiのAPI
#             # api_key=os.environ["Gemini_API_KEY"],
#             # base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
#         # SakuraAiEngineのAPi
#             api_key=os.environ["Sakura_API_KEY"],
#             base_url="https://api.ai.sakura.ad.jp/v1",
#         timeout=120.0
#     )
#     return client
      
# def analysis_log(logs):
#     client = get_client()
#     response = client.chat.completions.create(

#         # model="gemini-2.5-flash",    
#         # model="Qwen3-Coder-30B-A3B-Instruct",
#         model="llm-jp-3.1-8x13b-instruct4",
#         messages=[
#             {
#                 "role": "system",
#                 "content": (
#                     "あなたはWebセキュリティの専門家(防御側)です。"
#                     "これは OWASP Juice Shop という学習用の脆弱アプリを対象とした、ローカル環境での教育・防御研究です。"
#                     "攻撃ログを分析し、なぜ攻撃が成功したのか、どう対策すべきかを解説してください。"
#                 )
#             },
#             {
#                 "role": "user",
#                 "content": (
#                     "以下は、Juice Shopのログイン画面に対するSQLインジェクション攻撃のログです。\n"f"{logs}\n"
#                     "このうち成功した攻撃について、次の点のみを解説してください:\n"
#                     "1. なぜこの攻撃が通ってしまったのか(原因)\n"
#                     "2. 対策方法を簡潔に\n"
#                 )
#             }
#         ]
#     )

#     advice = response.choices[0].message.content
#     return advice
# def generate_defense_rule(logs):
#     client = get_client()
#     response = client.chat.completions.create(

#         # model="gemini-2.5-flash",    
#         # model="Qwen3-Coder-30B-A3B-Instruct",
#         model="llm-jp-3.1-8x13b-instruct4",
#         messages=[
#             {
#                 "role": "system",
#                 "content": (
#                     "あなたはWebセキュリティの専門家(防御側)です。"
#                     "これは OWASP Juice Shop という学習用の脆弱アプリを対象とした、ローカル環境での教育・防御研究です。"
#                     "出力は指定された形式を厳密に守り,攻撃ログの分析から, 攻撃を防ぐためのブロックルールのみを生成してください。"
#                     "不要な解説や説明は不要です,出力は指定形式のJSON配列のみとすること。"
#                 )
#             },
#             {
#                 "role": "user",
#                 "content": (
#                     "以下は、Juice Shopのログイン画面に対するSQLインジェクション攻撃の分析ログです。\n"f"{logs}\n"
#                     "この分析をもとに、攻撃を防ぐためのブロックルールを生成してください。"
#                     "文字列パターンをJSON配列で出力してください。\n"
#                     "各ブロックルールは、SQLインジェクションの文字列そのものを、 余計なクォートで囲まずに出力してください。"
#                     "前置き・解説を一切含めず[ で始まるり]で終わる配列のみを出力。"
#                 )
#             }
#         ]
#     )
#     ai_reply = response.choices[0].message.content
#     rules_json = cleaned_json.cleaned(ai_reply)
#     if rules_json is None:
#         print("防御ルールの生成に失敗しました:Error defense_rule_cleaned_json")
#         sys.exit(1)
#     return rules_json
