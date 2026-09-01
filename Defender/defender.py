# import blue_cloud_ai
from Defender import blue_local_ai
from .blue_local_ai import DefenseRule
from choice_ai import choice_ai_model
from Defender import defence_rate
import requests
import json
import sys


def main():
    logs = distinct_log()
    waf_rules = waf_score()
    gene_rules = waf_rules  #防御ルールを生成しなかった場合のスコアリング調整用にもともとのwafのルールをgene_rulesへ格納する
    updated_rules = waf_rules #生成・スコアリングをせずにWAFへのルールを送信した場合用のupdated_rulesの中身を定義
    #使用するAIを選択
    ai_model = choice_ai_model()
    
    while True:
        print("=====防御側操作=====")
        print("1：WAF通信ログ参照\n"
            "2：ログ分析 \n"
            "3：防御ルール生成\n"
            "4：防御ルールスコア調整\n"
            "5：WAFへの変更ルール送信\n"
            "6：現在のwafルール確認\n"
            "7：防御率計算\n"
            "8：処理の終了")
        user_action = input("実施する機能番号を入力してください:")
        match user_action:
            case "1":
                print("WAFの通信ログを確認します...")
                show_log()
            case "2":
                print("ログの分析を開始します...")
                analysis = defence_analysis(logs,ai_model)  
                print(analysis)
            case "3":
                print("防御ルールを生成します...")
                gene_rules = gene_blockrule(logs,waf_rules,ai_model)
                updated_rules = gene_rules #スコアリングを行わない場合にupdated_rulesを生成したルールの中身に変更
                print("生成された防御ルール",gene_rules)
            case "4":
                print("ルールのスコアリング調整を行います...")
                scored_rules = scoring_rules(logs,gene_rules,ai_model)
                a = input("このスコアリングをルールへ適応しますか?(y/n):") #ここで防御ルールが初期の一つしかない状態でスコアリング行うとエラー ※解決済み
                if a in["Y","y","yes"]:
                    updated_rules = update_rules(gene_rules,scored_rules)
            case "5":
                dicted_rules = attach_rules(updated_rules) #防御ルールの生成、スコアリングを行わない場合に辞書型に変換しようとするとエラー ※解決済み
                print("辞書変換後のルール",dicted_rules)
            case "6":
                res = show_waf_rules()
                print(res)
            case "7":
                print(defence_rate.defence_rate())
            case "8":

                print("処理を終了します...")
                break
            case _:
                print("エラーが起きました、処理を終了します...")
                sys.exit(1)

def distinct_log():
    success = []
    #WAFで記録されたログファイル読み込み
    with open("./Defender/waf_logs.json","r",encoding="utf-8") as f:
        log_data = json.load(f)
    
    for i in log_data:
        success.append(i["payloads"])
    #重複文字列削除
    success_dis =list(dict.fromkeys(success))  
    return success_dis

def waf_score():
    try:
        scoring_rules = requests.get("http://localhost:8000/show_rules")
        scoring_rules = scoring_rules.json()
        #json形式でルールを読み込んだ場合update_rules関数でエラーが起きるため、ルールを読み込んだ時点でPydanic形式に変換
        scoring_rules = [
            DefenseRule(**rule)
            for rule in scoring_rules
        ]
    except Exception as e:
        print(f"WAFからのルールが取得できなかったため処理を終了します...{e}")
        return sys.exit()
    
    return scoring_rules

def show_log():
    print(json.load(open("./Defender/waf_logs.json",encoding="utf-8")))

def defence_analysis(logs,ai_model):
    print("通信ログの分析を開始します...")
    # ai_ans = blue_cloud_ai.analysis_log(logs) #クラウドAIモデル
    ai_ans = blue_local_ai.analysis_log(logs,ai_model) #ローカルAIモデル
    return ai_ans

def gene_blockrule(logs,waf_rules,ai_model):
    # rules = blue_cloud_ai.generate_defense_rule(logs) #クラウドAIモデル
    gene_rules = blue_local_ai.generate_defense_rule(logs,waf_rules,ai_model) #ローカルAIモデル

    return gene_rules
  
def scoring_rules(logs,gene_rules,ai_model):
    scoring_rules = blue_local_ai.scoring_defense_rule(logs,gene_rules,ai_model) #ローカルAIモデル
    print("スコアリング対象の調整後のルール:",scoring_rules)
    return scoring_rules

def update_rules(gene_rules,scoring_rules):
    #スコアリング調整後のルールを生成した防御ルールへ適応する処理
    #genge_rulesは生成された防御ルール、scoring_rulesはスコアリング調整後のルール。
    update_rule = blue_local_ai.update_rule(gene_rules,scoring_rules) #ローカルAIモデル
    return update_rule
def show_waf_rules():
    res = requests.get("http://localhost:8000/show_rules")
    return res.json()
def attach_rules(update_rule):
    url = "http://localhost:8000/add_rule"

    try :
        res = requests.post(url,json=update_rule)
        return print("WAFの返答:",res.json())
    except Exception as e:
        print(f"ルール適応に失敗：やり直してください{e}")
        return None

if __name__ == "__main__":
    main()