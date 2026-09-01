from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List
from ai_model_config import get_ai_model
from Defender import defender
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

    # id: str = Field(description="ルールID")
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
                        "攻撃ログ"f"{logs}\n"
                        ""f"WAFルール{rules}\n"
                        """
                        攻撃ログ説明
                        payloads:ペイロード
                        score:ペイロード判定後スコア
                        alert:警告レベル
                        WAF:WAFの通信判定結果
                        detection_ID:検出ルールID,検出ルール名,ルールスコア
                        statuscode:ステータスコード
                        """
                        "現在のWAFはスコア合計35までは許可、40~80は警告レベル、80以上はブロックする仕様"                    
                        "スコアは0~100の範囲で調整すること"
                        "攻撃ログの結果から、危険なペイロードを許可している場合、対象ペイロードをブロックできるように、WAFルールと同じ形式で、欠如している防御ルールを生成"
                    )
                }
            ]   
        )
        res_reles = rules_numbering(response.rules)
        return res_reles
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
                        "攻撃ログ"f"{logs}\n"
                        ""f"WAFルール{rules}\n"
                        """
                        攻撃ログ説明
                        payloads:ペイロード
                        score:ペイロード判定後スコア
                        alert:警告レベル
                        WAF:WAFの通信判定結果
                        detection_ID:検出ルールID,検出ルール名,ルールスコア
                        statuscode:ステータスコード
                        """
                        "現在のWAFはスコア合計35までは許可、40~80は警告レベル、80以上はブロックする仕様"                    
                        "スコアは0~100の範囲で調整すること"
                        "攻撃ログの結果から、危険なペイロードを許可している場合、危険と判断し、detection_IDで検出されたルールのスコアを上げること"
                        "正常なペイロードをブロックしている場合は、誤検知と判断し、detection_IDで検出されたルールのスコアを下げること"
                    )
                }
            ]   
        )

        return response.rules
    except Exception as e:
        print(f"AIの応答にエラーが発生、処理を終了します：{e}")
        return sys.exit()
def rules_numbering(rules):
    old_rules = defender.show_waf_rules()
    new_rules = [rule.model_dump() for rule in rules]

    #既存IDの最大値を採番の起点にする（IDが連番でなくても衝突しない）
    existing_ids = [int(r["id"]) for r in old_rules if str(r.get("id", "")).isdigit()]
    next_id = max(existing_ids, default=0) + 1

    for n_rule in new_rules:
        #新規ルールごとに重複判定をリセットする（リセット漏れで以降のルールが破棄されるバグの修正）
        found = False
        for o_rule in old_rules:
            if o_rule["pattern"] == n_rule["pattern"]:
                found = True
                break
        if not found:
            n_rule["id"] = str(next_id).zfill(4)
            next_id += 1
            old_rules.append(n_rule)

    return old_rules

#生成orもともとの防御ルールにスコアリングしたルールの値を適応する処理
def update_rule(rules, scoring_rules):

    # scoring_rules はオブジェクトなので、ドットでアクセス
    update_rules = {
        i.id: i.score        # 角括弧 → ドットに変更
        for i in scoring_rules
    }
    print("スコアリング調整後のルール:", update_rules)

    # rules は辞書なので、こちらは角括弧のまま
    for i in rules:
        if i["id"] in update_rules:
            i["score"] = update_rules[i["id"]]

    return rules
  