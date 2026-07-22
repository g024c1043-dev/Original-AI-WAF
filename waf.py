from Defender import blue_ai
from flask import Flask,request,jsonify
import requests
import json

app = Flask(__name__)

JUICE_SHOP = "http://localhost:3000"
@app.route("/rest/user/login",methods=["POST"])


def waf_req():
    #ブロックルールの生成
    #JSON形式でattack.pyのリクエストを読み込み
    payload = request.get_json()
    #防御用ログ配列
    logs = []
    #引数で渡されたペイロードからemailだけを摘出
    email = payload.get("email","")
    #インジェクションのペイロードを防御AIに渡しブロックルール作成
    block_rule = blue_ai.generate_defense_rule(email)
    #ペイロードの中にブロックルールに該当するメールがあるか確認
    for rule in block_rule:
        if rule in email:
            print(f"[WAF]Block:(ルール{rule})")
            #ブロックされたペイロードも記録
            recode = {
                "ペイロード":email,
                "WAF":"Blocked",
                "ステータスコード":None,
            }
            logs.append(recode)
            return 403
    #WAFがブロックしなかったら通す
    print("[WAF]Allowed")
    #リクエスト転送
    response = requests.post(f"{JUICE_SHOP}/rest/user/login",json=payload)
    # 防御用ログファイルに書き込み
    recode = {
        "ペイロード":email,
        "WAF":"Allowed",
        "ステータスコード":response.status_code,
    }
    logs.append(recode)
    
    with open("Defender/waf_logs.json","w",encoding="utf-8") as f:
        json.dump(logs,f,ensure_ascii=False,indent=4)
    
    return response

if __name__ == "__main__":
    app.run(port=8000)  