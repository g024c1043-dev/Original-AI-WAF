from Attacker import attack
from Defender import defender
import choice_ai
import ai_model_config
import challengeAPI
import waf
import sys
import requests

def simulation():
    attacker_response = None
    while True:
        print("1：攻撃側操作\n"
              "2：防御側操作\n"
              "3：WAFルール表示\n"
              "4：Juice Shop攻略\n"
              "5：自動攻防ループ\n"
              "6：処理の終了")
        user_action = input("操作を選択してください:")
        match user_action:
            case "1":
                #attack.pyに攻撃とペイロードを生成させる
                attacker_response = attack.main(attacker_response)
            case "2":
                defender_response = defender.main()
            case "3":
                print("WAFの現在のルールを表示します...")
                res = requests.get("http://localhost:8000/show_rules")
                print("現在のルール：",res.json())
            case "4":
                print(challengeAPI.api_solved())
            case "5":
                simulater_loop(attacker_response)
            case "6":
                print("処理を終了します...")
                sys.exit(1)
            case _:
                print("エラーが起きました、処理を終了します...")
                sys.exit(1)
def simulater_loop(attacker_response):
    #AI環境選択
    ai_model = choice_ai.choice_ai_model()
    #攻撃生成事前準備
    print(ai_model)
    #ループ処理
    for i in range(3):
        print(f"{i+1}回目攻防ループ")   
        attacker_loop(ai_model)
        defender_loop(ai_model)

def attacker_loop(ai_model):
    logs = attack.load_logs()
    #攻撃生成
    attack_payloads = attack.generate_payload(logs,ai_model)
    #生成に失敗した場合はこの周回の攻撃をスキップ（Noneのまま攻撃処理へ渡さない）
    if not attack_payloads:
        print("攻撃ペイロードの生成に失敗したため、この周回の攻撃をスキップします...")
        return
    print(attack_payloads)
    #攻撃
    attack.payload_p(attack_payloads)
def defender_loop(ai_model):
    #wafの通信ログ読み取り
    logs = defender.distinct_log()
    #現在のwafルールの読み取り
    waf_rule = defender.waf_score()
    #ログファイル分析
    ai_analysis = defender.defence_analysis(logs,ai_model)
    #分析結果から防御ルールの生成
    generate_rule = defender.gene_blockrule(logs,waf_rule,ai_model)
    #ルールスコアの調整
    scored_rule = defender.scoring_rules(logs,generate_rule,ai_model)
    #既存、生成したルールへスコア変更後のルール適応
    apdate_rule = defender.update_rules(generate_rule,scored_rule)
    #wafへの送信
    defender.attach_rules(apdate_rule)
if __name__ == "__main__":
    simulation()
