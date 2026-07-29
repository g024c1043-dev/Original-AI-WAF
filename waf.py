# from Defender import blue_ai
from flask import Flask,request,jsonify
import requests
import json

app = Flask(__name__)
block_rule = []
JUICE_SHOP = "http://localhost:3000"
@app.route("/rest/user/login",methods=["POST"])
def waf_req():
    #ブロックルールの生成
    #JSON形式でattack.pyのリクエストを読み込み
    payload = request.get_json()
    #引数で渡されたペイロードからemailだけを摘出
    email = payload.get("email","")
    #インジェクションのペイロードを防御AIに渡しブロックルール作成
    
    #ペイロードの中にブロックルールに該当するメールがあるか確認
    for rule in block_rule:
        if rule in email:
            print(f"[WAF]Block:(ルール{rule})")
            #ブロックされたペイロードも記録
            recode = {
                "ペイロード":email,
                "WAF":"Blocked",
                "ステータスコード":403,
            }
            save_log(recode)
            return jsonify({"error":"アクセス拒否"}),403
        
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
    save_log(recode)
    #JuiceShopから帰ってきたレスポンスをflaskがわかる形式にしてHTTPレスポンスとして組み立て、クライアントに返す
    try:
        return jsonify(response.json()),response.status_code
    except:
        return response.text,response.status_code
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
    data=request.get_json()      
    rules = data.get("rules",[])
    block_rule.extend(rules)
    print(f"[WAF] ルールを追加: {rules}")
    print(f"[WAF] 現在のルール: {block_rule}")

    return jsonify({"message": f"{len(rules)}個のルールを追加しました"}), 200
if __name__ == "__main__":
    app.run(port=8000)  