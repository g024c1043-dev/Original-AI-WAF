import requests
import json
import sys
from Attacker import red_cloud_ai
from Attacker import red_local_ai 
from choice_ai import choice_ai_model

#メイン関数(引数same_payloadは過去に生成したペイロードを使用して攻撃する場合に使用する)
def main(same_payload):
    #ログファイル読み込み
    logs = load_logs()
    #攻撃を生成せずにcase2を実行する場合の定義
    ai_reply = None
    #モデルを選択
    ai_model = choice_ai_model()

    while True:
        print("=====攻撃側操作=====")
        print("1：攻撃ペイロード生成\n"
              "2：生成したペイロードで攻撃\n"
              "3：攻撃側操作終了\n")
        
        user_action = input("実施する機能番号を入力してください:")

        match user_action:
            case "1":
        
                #logsの中身がない場合（攻撃を一度も行ってない場合は攻撃結果を参照せずゼロから攻撃を生成する
                if logs == []:
                    ai_reply = generate_payload(logs,ai_model)
                    print(f"生成されたペイロード：{ai_reply}")

                else:
                    b = input("攻撃結果ログが存在します：\n"
                              "ログ結果を使用し新しい攻撃ペイロードを生成しますか？(y/n):")
                    if b in["Y","y","yes"]:
                        ai_reply = generate_payload(logs,ai_model)
                        print(ai_reply)
            case "2":
                c = input("※すでに攻撃済みの場合のみ※\n前回と同じ攻撃ペイロードを使用しますか？(y/n):")
                #直近で生成したペイロードと一度生成したペイロードのどちらも存在しない場合
                if not ai_reply and not same_payload:
                    print("攻撃ペイロードが存在しません...")
                #同じペイロードを使用した攻撃
                elif c in ["Y","y","yes"]:
                    if same_payload:
                        logs = payload_p(same_payload)
                    else:
                        print("前回のペイロードが存在しないため、生成したペイロードで攻撃を行います...")
                        logs = payload_p(ai_reply)
                #直近で生成したペイロードを使用した場合
                elif ai_reply and c in ["N","n","no"]:
                    print("攻撃ペイロードを使用して攻撃を開始します...")
                    logs = payload_p(ai_reply)
                    print("新しい攻撃ペイロードを生成する場合は再度攻撃ペイロードを生成を選択してください")
                else:
                    print("エラーが発生したため処理を終了します...")
                    break
            case "3":
                print("攻撃側の処理を終了します...")
                return ai_reply
            case _:
                print("エラーが起きました、処理を終了します...")
                sys.exit(1)

def load_logs():

    with open("./Attacker/attack_logs.json","r",encoding="utf-8") as f:
            log_data = json.load(f)
    
            if not log_data:
                logs = []
            else:
                logs = json.dumps(log_data,ensure_ascii=False,indent=2)

    return logs

def generate_payload(logs,use_ai):
    
    #攻撃ペイロードを生成
    try:
        ai_reply = red_local_ai.payload_ganerate(logs,use_ai) #ローカルAI使用
        # ai_reply = red_cloud_ai.payload_ganerate(logs) #クラウドAI使用
        return ai_reply
    except:
        print("--攻撃文生成時にエラーが発生--")

        #攻撃ペイロードを生成するのに失敗した場合3回までリトライする処理
        for i in range(3):
            try:
                print(f"再試行中：{i+1}回目...")
                ai_reply = red_local_ai.payload_ganerate(logs,use_ai) #ローカルAI使用
                # ai_reply = red_cloud_ai.payload_ganerate(logs) #クラウドAI使用
                return ai_reply
            except:
                print(f"{i+1}回目の再試行処理が失敗...")

        print("再試行でもエラーが発生したため処理を中断します...")
        return None

#攻撃用ペイロード
def payload_p(ai_reply):
    logs = []
    url = "http://localhost:8000/rest/user/login"  # 攻撃対象のURL
    nomal_emails = [
        "test@example.com",
        "yamada.taro@gmail.com",
        "O'Brien@example.com",        # 'を含む正常なメール（実験用
        "info@company.co.jp",
        "user_123@mail.net",
    ]

    #生成に失敗(None)、または生成物がリストでない場合は空リスト扱いにして落ちないようにする
    if not isinstance(ai_reply, list):
        if ai_reply is not None:
            print(f"生成ペイロードの形式が不正です（{type(ai_reply).__name__}）。正常メールのみで実行します...")
        else:
            print("生成された攻撃ペイロードが存在しません。正常メールのみで実行します...")
        ai_reply = []

    print(f"生成したペイロード:{ai_reply + nomal_emails}")
    #email_payloadsに生成したメールアドレスを入れるパスワードはaaa固定
    email_payloads = ai_reply + nomal_emails
    pass_payloads = "aaa"
    for i in email_payloads:
        print(f"\n実行中[email]:{i}" )
        payload = {
                    "email":i,
                    "password":pass_payloads
                }
        response = requests.post(url,json=payload)
        judged = payload_judgement(response,i)
        logs.append(judged)
    #書き込み関数    
    weite_log(logs)

    return logs
def payload_judgement(response,i):
        #攻撃ステータスコードが403だったら記録
        if response.status_code == 403:
            recode = {
                "ペイロード": i,
                "WAF":"Blocked",
                "ステータスコード":403,
                "攻撃結果": False,
            }
            print(f"インジェクション攻撃がブロックされました:status_code:{response.status_code}")
            return recode
        elif response.status_code == 200:
            #WAFにブロックされず通過した場合ここで攻撃を記録
            recode = {
                "ペイロード": i,
                "WAF":"Allowed",
                "ステータスコード": response.status_code,
                "攻撃結果":True,
            }
            print(f"インジェクション攻撃が成功しました:status_code:{response.status_code}")
            return recode
        elif response.status_code == 500:
            analyze = analyze_500error(response.text)
            #WAFにブロックされず通過した場合ここで攻撃を記録
            recode = {
                "ペイロード": i,
                "WAF":"Allowed",
                "ステータスコード": response.status_code,
                "攻撃結果":False,
            }
            print(f"{analyze}:status_code:{response.status_code}")
            return recode
        else:
            recode = {
                "ペイロード": i,
                "WAF":"Allowed",
                "ステータスコード": response.status_code,
                "攻撃結果":False,
            }
            print(f"WAFは通過したがインジェクション攻撃は失敗:status_code:{response.status_code}")
            return recode
        
#ステータスコードが500の場合、脆弱性の発見かサーバーエラーかを判定する
def analyze_500error(res_text):
    
    vulnerability = [
        "SQLITE_ERROR",
        "SequelizeDatabaseError",
        "syntax error",
        "SELECT",
        "FROM Users", 
    ]

    for i in vulnerability:
        if i in res_text:
            return "脆弱性の兆候あり"
        
    return "サーバーエラー(詳細不明)"
def weite_log(logs):
    #攻撃ログをlogs.jsonファイルに書き込み
    with open("./Attacker/attack_logs.json","w",encoding="utf-8") as f:
        json.dump(logs,f,ensure_ascii=False,indent=4)

    a = input("攻撃結果ログを表示しますか？(y/n):")
    if a in["Y","y","yes"]:
        for i in logs:
            print(f"攻撃ログ：{i}\n")
    
#ユーザーデータ取得
def token_p(token):
    myheaders = {"Authorization":f"Bearer {token}"}
    rsa_auth = requests.get("http://localhost:3000/api/Users",headers=myheaders)
    print("ステータスコード:",rsa_auth.status_code)
    print("全ユーザー情報:", rsa_auth.json())

#防御率計算は Defender/defence_rate.py に一本化（重複実装を削除）

if __name__ == "__main__":
    main()

# import requests
# import json
# import sys
# from Attacker import red_cloud_ai
# from Attacker import red_local_ai 
# from choice_ai import choice_ai_model

# #メイン関数(引数same_payloadは過去に生成したペイロードを使用して攻撃する場合に使用する)
# def main(same_payload):
#     #ログファイル読み込み
#     logs = load_logs()
#     #攻撃を生成せずにcase2を実行する場合の定義
#     ai_reply = None
#     #モデルを選択
#     ai_model = choice_ai_model()
#     while True:
#         print("=====攻撃側操作=====")
#         print("1：攻撃ペイロード生成\n"
#               "2：生成したペイロードで攻撃\n"
#               "3：攻撃側操作終了\n")
        
#         user_action = input("実施する機能番号を入力してください:")

#         match user_action:
#             case "1":
        
#                 #logsの中身がない場合（攻撃を一度も行ってない場合は攻撃結果を参照せずゼロから攻撃を生成する
#                 if logs == []:
#                     ai_reply = generate_payload(logs,ai_model)
#                     print(f"生成されたペイロード：{ai_reply}")

#                 else:
#                     b = input("攻撃結果ログが存在します：\n"
#                               "ログ結果を使用し新しい攻撃ペイロードを生成しますか？(y/n):")
#                     if b in["Y","y","yes"]:
#                         ai_reply = generate_payload(logs,ai_model)
#                         print(ai_reply)
#             case "2":
#                 c = input("※すでに攻撃済みの場合のみ※\n前回と同じ攻撃ペイロードを使用しますか？(y/n):")
#                 #直近で生成したペイロードと一度生成したペイロードのどちらも存在しない場合
#                 if not ai_reply and not same_payload:
#                     print("攻撃ペイロードが存在しません...")
#                 #同じペイロードを使用した攻撃
#                 elif c in ["Y","y","yes"]:
#                     if same_payload:
#                         logs = payload_p(same_payload)
#                     else:
#                         print("前回のペイロードが存在しないため、生成したペイロードで攻撃を行います...")
#                         logs = payload_p(ai_reply)
#                 #直近で生成したペイロードを使用した場合
#                 elif ai_reply and c in ["N","n","no"]:
#                     print("攻撃ペイロードを使用して攻撃を開始します...")
#                     logs = payload_p(ai_reply)
#                     print("新しい攻撃ペイロードを生成する場合は再度攻撃ペイロードを生成を選択してください")
#                 else:
#                     print("エラーが発生したため処理を終了します...")
#                     break
#             case "3":
#                 print("攻撃側の処理を終了します...")
#                 return ai_reply
#             case _:
#                 print("エラーが起きました、処理を終了します...")
#                 sys.exit(1)

# def load_logs():

#     with open("./Attacker/attack_logs.json","r",encoding="utf-8") as f:
#             log_data = json.load(f)
    
#             if not log_data:
#                 logs = []
#             else:
#                 logs = json.dumps(log_data,ensure_ascii=False,indent=2)

#     return logs

# def generate_payload(logs,use_ai):

#     #攻撃ペイロードを生成
#     try:
#         ai_reply = red_local_ai.payload_ganerate(logs,use_ai) #ローカルAI使用
#         # ai_reply = red_cloud_ai.payload_ganerate(logs) #クラウドAI使用
#         return ai_reply
#     except:
#         print("--攻撃文生成時にエラーが発生--")

#         #攻撃ペイロードを生成するのに失敗した場合3回までリトライする処理
#         for i in range(3):
#             try:
#                 print(f"再試行中：{i+1}回目...")
#                 ai_reply = red_local_ai.payload_ganerate(logs,use_ai) #ローカルAI使用
#                 # ai_reply = red_cloud_ai.payload_ganerate(logs) #クラウドAI使用
#                 return ai_reply
#             except:
#                 print(f"{i+1}回目の再試行処理が失敗...")

#         print("再試行でもエラーが発生したため処理を中断します...")
#         return None

# #攻撃用ペイロード
# def payload_p(ai_reply):
#     logs = []
#     url = "http://localhost:8000/rest/user/login"  # 攻撃対象のURL
#     nomal_emails = [
#         "test@example.com",
#         "yamada.taro@gmail.com",
#         "O'Brien@example.com",        # 'を含む正常なメール（実験用
#         "info@company.co.jp",
#         "user_123@mail.net",
#     ]

#     print(f"生成したペイロード:{ai_reply + nomal_emails}")
#     #email_payloadsに生成したメールアドレスを入れるパスワードはaaa固定
#     email_payloads = ai_reply + nomal_emails
#     pass_payloads = "aaa"
#     for i in email_payloads:
#         print(f"\n実行中[email]:{i}" )
#         payload = {
#                     "email":i,
#                     "password":pass_payloads
#                 }
#         response = requests.post(url,json=payload)
#         #攻撃ステータスコードが403だったら記録
#         if response.status_code == 403:
#             recode = {
#                 "ペイロード": i,
#                 "WAF":"Blocked",
#                 "ステータスコード":403,
#                 "攻撃結果": False,
#             }
#             logs.append(recode)
#             print(f"インジェクション攻撃がブロックされました:status_code:{response.status_code}")
#         elif response.status_code == 200:
#             #WAFにブロックされず通過した場合ここで攻撃を記録
#             recode = {
#                 "ペイロード": i,
#                 "WAF":"Allowed",
#                 "ステータスコード": response.status_code,
#                 "攻撃結果":True,
#             }
#             logs.append(recode) #logs配列に入れる
#             print(f"インジェクション攻撃が成功しました:status_code:{response.status_code}")
#         elif response.status_code == 500:
#             analyze = analyze_500error(response.text)
#             #WAFにブロックされず通過した場合ここで攻撃を記録
#             recode = {
#                 "ペイロード": i,
#                 "WAF":"Allowed",
#                 "ステータスコード": response.status_code,
#                 "攻撃結果":False,
#             }
#             logs.append(recode) #logs配列に入れる
#             print(f"{analyze}:status_code:{response.status_code}")
#         else:
#             recode = {
#                 "ペイロード": i,
#                 "WAF":"Allowed",
#                 "ステータスコード": response.status_code,
#                 "攻撃結果":False,
#             }
#             logs.append(recode) #logs配列に入れる
#             print(f"WAFは通過したがインジェクション攻撃は失敗:status_code:{response.status_code}")
#     #攻撃ログをlogs.jsonファイルに書き込み
#     with open("./Attacker/attack_logs.json","w",encoding="utf-8") as f:
#         json.dump(logs,f,ensure_ascii=False,indent=4)

#     a = input("攻撃結果ログを表示しますか？(y/n):")
#     if a in["Y","y","yes"]:
#         for i in logs:
#             print(f"攻撃ログ：{i}\n")

#     return logs

# #ステータスコードが500の場合、脆弱性の発見かサーバーエラーかを判定する
# def analyze_500error(res_text):
    
#     vulnerability = [
#         "SQLITE_ERROR",
#         "SequelizeDatabaseError",
#         "syntax error",
#         "SELECT",
#         "FROM Users", 
#     ]

#     for i in vulnerability:
#         if i in res_text:
#             return "脆弱性の兆候あり"
        
#     return "サーバーエラー(詳細不明)"

# #ユーザーデータ取得
# def token_p(token):
#     myheaders = {"Authorization":f"Bearer {token}"}
#     rsa_auth = requests.get("http://localhost:3000/api/Users",headers=myheaders)
#     print("ステータスコード:",rsa_auth.status_code)
#     print("全ユーザー情報:", rsa_auth.json())

# #防御率計算
# def defence_rate(logs):
#     total = len(logs)
#     block = sum(1 for i in logs if i["WAF"] == "Blocked")
#     return block/total

# if __name__ == "__main__":
#     main()
