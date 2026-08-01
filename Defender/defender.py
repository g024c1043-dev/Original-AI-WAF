import blue_cloud_ai
import blue_local_ai
import requests
import json

def distinct_log():
    success = []
    #WAFで記録されたログファイル読み込み
    with open("./Defender/waf_logs.json","r",encoding="utf-8") as f:
        log_data = json.load(f)
    #ステータスコード200のみのペイロードをリストへ
    for i in log_data:
        if i["ステータスコード"] == 200:
            success.append(i["ペイロード"])
    #重複文字列削除
    success_dis =list(set(success))  
    return success_dis
def gene_blockrule():
    logs = distinct_log()
    a = input("WAFの通信ログを確認しますか？(y/n):")
    if a in["Y","y","yes"]:
        print(json.load(open("./Defender/waf_logs.json",encoding="utf-8")))
    b = input("通信ログから危険性のあるログを分析しますか？(y/n):")
    if b in["Y","y","yes"]:
        print("通信ログの分析を開始します...")
        # ai_ans = blue_cloud_ai.analysis_log(logs) #クラウドAIモデル
        ai_ans = blue_local_ai.analysis_log(logs) #ローカルAIモデル
        print(ai_ans)
    c = input("通信ログから防御ルールを生成しますか？(y/n):")
    if c in["Y","y","yes"]:
        # rules = blue_cloud_ai.generate_defense_rule(logs) #クラウドAIモデル
        rules = blue_local_ai.generate_defense_rule(logs) #ローカルAIモデル
        print("生成された防御ルール:",rules)
        d = input("生成されたルールをWAFのブロックルールへ追加しますか?(y/n):")
        if d in["Y","y","yes"]:
            #wafへのブロックルール追加リクエスト
            url = "http://localhost:8000/add_rule"
            res = requests.post(
                #json内のrulesというキーに生成されたルールを渡す
                url,json={"rules":rules}
            )
            print("WAFの返答",res.json())
    
if __name__ == "__main__":
    gene_blockrule()