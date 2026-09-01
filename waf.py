# from Defender import blue_ai
from flask import Flask,request,jsonify
from pydantic import BaseModel, ValidationError, field_validator
import requests
import json
import re

app = Flask(__name__)
block_rule = []
#waf_scoring.jsonをscoing_rulesに読み込む
with open("waf_scoring.json", "r", encoding="utf-8") as f:
    scoring_rules = json.load(f)


#/add_ruleで受け取るルールの検証用モデル
class ScoringRule(BaseModel):
    pattern: str
    score: int
    name: str = ""
    id: str = ""

    @field_validator("pattern")
    @classmethod
    def _validate_regex(cls, v):
        #壊れた正規表現をルールに取り込むと以降の全リクエストが500になるため、ここで弾く
        try:
            re.compile(v)
        except re.error as e:
            raise ValueError(f"無効な正規表現パターンです: {v!r} ({e})")
        return v

JUICE_SHOP = "http://localhost:3000"

#実験（閾値スイープ）で決定した判定スコアのしきい値
BLOCK_THRESHOLD = 35   # score >= これ でブロック(403)
WARN_THRESHOLD  = 20   # BLOCK未満だが score >= これ は「通すが要注意(warning)」としてログに残す
CRITICAL_SCORE  = 50   # ブロックの中でも高リスクの表示区分

@app.route("/rest/user/login",methods=["POST"])
def waf_req():

    #JSON形式でattack.pyのリクエストを読み込み
    payload = request.get_json()
    #引数で渡されたペイロードからemailだけを摘出
    email = payload.get("email","")
    score = 0
    pattern_ID = []
    #waf_scoringに記載されているルールと照合し、スコアを加算
    for rule in scoring_rules:
        #不正なパターンやemailの型崩れで1ルールがこけても、WAF全体を止めない
        try:
            if re.search(rule["pattern"], email, re.IGNORECASE):
                score += rule["score"]
                pattern_ID.append((rule.get("id","No detection"), rule.get("name","No detection"),rule.get("score","No detection")))
        except (re.error, TypeError, KeyError) as e:
            print(f"[WAF] ルール適用をスキップしました: {rule} ({e})")
            continue

    #判定：BLOCK_THRESHOLD 未満は通過（Juice Shopへ転送）、以上はブロック
    if score < BLOCK_THRESHOLD:
        headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
            }
        response = requests.post(f"{JUICE_SHOP}/rest/user/login",json=payload,headers=headers)

        #WARN_THRESHOLD以上は通すが「要注意(warning)」としてログに残す
        if score < WARN_THRESHOLD:
            level = "low-level"
        else:
            level = "warning"

        recode = {
                "payloads":email,
                "score":score,
                "alert":level,
                "WAF":"Allowed",
                "detection_ID": pattern_ID,
                "statuscode":response.status_code,
        }
        save_log(recode)

        try:
            return jsonify(response.json()),response.status_code

        except Exception as e:
            print(f"jsonエラー発生: {e}")
            return response.text,response.status_code

    #BLOCK_THRESHOLD以上はブロック
    else:
        if score < CRITICAL_SCORE:
           level = "high-level"
        else:
            level = "critical"

        recode = {
                "payloads":email,
                "score":score,
                "alert":level,
                "WAF":"Blocked",
                "detection_ID": pattern_ID,
                "statuscode":403,
        }

        save_log(recode)

        return jsonify({"error":"アクセス拒否"}),403

def save_log(log):
    #wafのログを一度読み込んで追記
    try:
        with open("./Defender/waf_logs.json","r",encoding="utf-8") as f:
            log_data = json.load(f)
    except:
        log_data = []
        
    log_data.append(log)  

    with open("Defender/waf_logs.json", "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=4)

#WAFの現在のルールを表示
@app.route("/show_rules",methods=["GET"])
def show_logs():
    return jsonify(scoring_rules)       

#ブロックルールを追加するための入口       
@app.route("/add_rule",methods=["POST"])
def add_rule():
    global scoring_rules
    body = request.get_json(silent=True)

    #JSON配列以外は受け付けない
    if not isinstance(body, list):
        return jsonify({"error": "ルールはJSON配列で送信してください"}), 400

    #pattern/scoreの欠落や壊れた正規表現をここで検証し、既存ルールは維持する
    try:
        validated = [ScoringRule(**rule).model_dump() for rule in body]
    except (ValidationError, TypeError) as e:
        print(f"[WAF] ルール検証に失敗しました: {e}")
        return jsonify({"error": "ルールの検証に失敗しました", "detail": str(e)}), 400

    scoring_rules = validated
    print(f"[WAF] 現在のルール: {scoring_rules}")
    return jsonify({"message": f"{len(scoring_rules)}個のルールを追加・変更しました"})

if __name__ == "__main__":
    app.run(port=8000)
    