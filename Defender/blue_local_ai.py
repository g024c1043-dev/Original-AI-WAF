from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List
from ai_model_config import get_ai_model
import instructor
import json
import os
import sys
import cleaned_json

load_dotenv()
#スコアリング用のBaseModel
class Block_Scoring_Rule(BaseModel):

    id: str = Field(description="変更対象のルールID")
    score: int = Field(description="変更後のスコア")    
    
class ScoringRules(BaseModel):

    rules: List[Block_Scoring_Rule] = Field(description="既存の防御ルールに対する変更後のスコア一覧")

#ルール生成用のBaseModel
class DefenseRule(BaseModel):

    id: str = Field(description="ルールID")
    pattern: str = Field(description="ルールのパターン")
    score: int = Field(description="ルールのスコア")
    name: str = Field(description="ルールの名前")

class Generate_Defense_Rules(BaseModel):

    rules: List[DefenseRule] = Field(description="既存のルールへのルール追加後のスコア一覧")

def get_client(use_ai_model):

    ai_config = use_ai_model
    client = OpenAI(
        api_key=ai_config["api_key"],
        base_url=ai_config["base_url"],
        timeout=120,

    )
    models = ai_config["model"]

    return client,models
#解説用AI関数
def analysis_log(logs,ai_model):

    client,attach_ai = get_client(ai_model)
    try:
        response = client.chat.completions.create(

            model=attach_ai,
            max_tokens=2000,
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
    except Exception as e:
        print(f"AIの応答にエラーが発生、処理を終了します：{e}")
        return sys.exit()
#防御ルール生成用AI関数
def generate_defense_rule(logs,rules,ai_model):
    attach_client,attach_ai = get_client(ai_model)
    client = instructor.from_openai(client=attach_client,mode=instructor.Mode.MD_JSON)
    try:
        
        response = client.chat.completions.create(

            model=attach_ai,
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
    except Exception as e:
        print(f"AIの応答にエラーが発生、処理を終了します：{e}")
        return sys.exit()
#防御ルールスコアリング調整用AI関数
def scoring_defense_rule(logs,rules,ai_model):
    attach_client,attach_ai = get_client(ai_model)
    client = instructor.from_openai(client=attach_client,mode=instructor.Mode.MD_JSON)
    try:
        response = client.chat.completions.create(

            model=attach_ai,
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
    except Exception as e:
        print(f"AIの応答にエラーが発生、処理を終了します：{e}")
        return sys.exit()

#生成orもともとの防御ルールにスコアリングしたルールの値を適応する処理
def update_rule(rules,scoring_rules):

    #スコアリングでスコアを変更した分の辞書を作成
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
  