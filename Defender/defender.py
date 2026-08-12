import blue_cloud_ai
import blue_local_ai
import requests
import json
import sys
from blue_local_ai import DefenseRule

def main():
    logs = distinct_log()
    waf_rules = waf_score()
    gene_rules = waf_rules  #防御ルールを生成しなかった場合のスコアリング調整用にもともとのwafのルールをgene_rulesへ格納する
    updated_rules = waf_rules #生成・スコアリングをせずにWAFへのルールを送信した場合用のupdated_rulesの中身を定義
    while True:

        print("1：WAF通信ログ参照\n"
            "2：ログ分析 \n"
            "3：防御ルール生成\n"
            "4：防御ルールスコア調整\n"
            "5：WAFへの変更ルール送信\n"
            "6：処理の終了")
        user_action = input("実施する機能番号を入力してください。")
        match user_action:
            case "1":
                print("WAFの通信ログを確認します...")
                show_log()
            case "2":
                print("ログの分析を開始します...")
                analysis = defence_analysis(logs)  
                print(analysis)
            case "3":
                print("防御ルールを生成します...")
                gene_rules = gene_blockrule(logs,waf_rules)
                updated_rules = gene_rules #スコアリングを行わない場合にupdated_rulesを生成したルールの中身に変更
                print("生成された防御ルール",gene_rules)
            case "4":
                print("ルールのスコアリング調整を行います...")
                scored_rules = scoring_rules(logs,gene_rules)
                a = input("このスコアリングをルールへ適応しますか?(y/n):") #ここで防御ルールが初期の一つしかない状態でスコアリング行うとエラー
                if a in["Y","y","yes"]:
                    updated_rules = update_rules(gene_rules,scored_rules)
            case "5":
                dicted_rules = dict_rules(updated_rules) #防御ルールの生成、スコアリングを行わない場合に辞書型に変換しようとするとエラー
                print("辞書変換後のルール",dicted_rules)
            case "6":
                print("処理を終了します...")
                sys.exit(1)
            case _:
                print("エラーが起きました、処理を終了します...")
                sys.exit(1)

def distinct_log():
    success = []
    #WAFで記録されたログファイル読み込み
    with open("./Defender/waf_logs.json","r",encoding="utf-8") as f:
        log_data = json.load(f)
    
    for i in log_data:
        success.append(i["ペイロード"])
    #重複文字列削除
    success_dis =list(dict.fromkeys(success))  
    return success_dis

def waf_score():
    #waf_scoring.jsonを読み込む
    with open("waf_scoring.json", "r", encoding="utf-8") as f:
        scoring_rules = json.load(f) 

    #json形式でルールを読み込んだ場合update_rules関数でエラーが起きるため、ルールを読み込んだ時点でPydanic形式に変換
    scoring_rules = [
        DefenseRule(**rule)
        for rule in scoring_rules
    ]

    return scoring_rules

def show_log():
    print(json.load(open("./Defender/waf_logs.json",encoding="utf-8")))

def defence_analysis(logs):
    print("通信ログの分析を開始します...")
    # ai_ans = blue_cloud_ai.analysis_log(logs) #クラウドAIモデル
    ai_ans = blue_local_ai.analysis_log(logs) #ローカルAIモデル
    return ai_ans

def gene_blockrule(logs,waf_rules):
    # rules = blue_cloud_ai.generate_defense_rule(logs) #クラウドAIモデル
    gene_rules = blue_local_ai.generate_defense_rule(logs,waf_rules) #ローカルAIモデル

    return gene_rules
  
def scoring_rules(logs,gene_rules):
    scoring_rules = blue_local_ai.scoring_defense_rule(logs,gene_rules) #ローカルAIモデル
    print("スコアリング対象の調整後のルール:",scoring_rules)
    return scoring_rules

def update_rules(gene_rules,scoring_rules):
    #スコアリング調整後のルールを生成した防御ルールへ適応する処理
    #genge_rulesは生成された防御ルール、scoring_rulesはスコアリング調整後のルール。
    update_rule = blue_local_ai.update_rule(gene_rules,scoring_rules) #ローカルAIモデル
    return update_rule

def dict_rules(update_rule):
    if isinstance(update_rule,dict):
        print("すでに辞書型です。")
        return update_rule
    else:
        rules_dict = [rule.model_dump() for rule in update_rule]
        return rules_dict
if __name__ == "__main__":
    main()