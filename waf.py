# from Defender import blue_ai
from flask import Flask,request,jsonify
import requests
import json
import re

app = Flask(__name__)
block_rule = []
#waf_scoring.jsonをscoing_rulesに読み込む
with open("waf_scoring.json", "r", encoding="utf-8") as f:
    scoring_rules = json.load(f) 

JUICE_SHOP = "http://localhost:3000"

@app.route("/rest/user/login",methods=["POST"])
def waf_req():

    #JSON形式でattack.pyのリクエストを読み込み
    payload = request.get_json()
    #引数で渡されたペイロードからemailだけを摘出
    email = payload.get("email","")
    score = 0
    #waf_scoringに記載されているルールと照合し、スコアを加算
    for rule in scoring_rules:
        if re.search(rule["pattern"], email,re.IGNORECASE):
            score += rule["score"]

    #スコア40以下の通信判定
    if score <= 40:

        response = requests.post(f"{JUICE_SHOP}/rest/user/login",json=payload)

        if score <= 20:
            level = "low-level"
        else:
            level = "medium-level"

        recode = {
                "ペイロード":email,
                "スコア":score,
                "アラートレベル":level,
                "WAF":"Allowed",
                "ステータスコード":response.status_code,
        }
        save_log(recode)
        
        try:
            return jsonify(response.json()),response.status_code
        except Exception as e:
            print(f"jsonエラー発生: {e}")
            return response.text,response.status_code
        
    #スコア40以上の通信判定
    else:
        if score <= 80:
           level = "high-level"
        else:
            level = "WARNING"

        recode = {
                "ペイロード":email,
                "スコア":score,
                "アラートレベル":level,
                "WAF":"blocked",
                "ステータスコード":403,
        }

        save_log(recode)

        try:
            return jsonify({"error":"アクセス拒否"}),403
        except Exception as e:
            print(f"jsonエラー発生: {e}")
            return response.text,response.status_code

    # #ペイロードの中にブロックルールに該当するメールがあるか確認
    # for rule in block_rule:
    #     if rule in email:
    #         print(f"[WAF]Block:(ルール{rule})")
    #         #ブロックされたペイロードも記録
    #         recode = {
    #             "ペイロード":email,
    #             "WAF":"Blocked",
    #             "ステータスコード":403,
    #         }
    #         save_log(recode)
    #         return jsonify({"error":"アクセス拒否"}),403
        
    # #WAFがブロックしなかったら通す
    # print("[WAF]Allowed")
    # #リクエスト転送
    # response = requests.post(f"{JUICE_SHOP}/rest/user/login",json=payload)
    # # 防御用ログファイルに書き込み
    # recode = {
    #     "ペイロード":email,
    #     "WAF":"Allowed",
    #     "ステータスコード":response.status_code,
    # }
    # save_log(recode)
    # #JuiceShopから帰ってきたレスポンスをflaskがわかる形式にしてHTTPレスポンスとして組み立て、クライアントに返す
    # try:
    #     return jsonify(response.json()),response.status_code
    # except:
    #     return response.text,response.status_code
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
        
#ブロックルールを追加するための入口       
@app.route("/add_rule",methods=["POST"])
def add_rule():
    global scoring_rules
    scoring_rules =request.get_json()
    
    #リクエストからとってきたJSONファイルからrulesというキーの値を取得
    # rules = data.get("rules",[])
    # #block_ruleに追加する
    # block_rule.extend(rules)
    # print(f"[WAF] ルールを追加: {rules}")
    print(f"[WAF] 現在のルール: {scoring_rules}")

    return jsonify({"message": f"{len(scoring_rules)}個のルールを追加・変更しました"})
if __name__ == "__main__":
    app.run(port=8000)
    