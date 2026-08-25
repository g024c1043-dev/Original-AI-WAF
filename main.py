from Attacker import attack
from Defender import defender
import choice_ai
import ai_model_config
import challengeAPI
import waf
import sys


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
                waf.show_logs()      
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
    choice = choice_ai.choice_ai_model()
    ai_model = ai_model_config.get_ai_model(choice)
    #攻撃生成事前準備
    logs = attack.load_logs()
    print(ai_model)
    #ループ処理
    for i in range(3):
        print(f"{i+1}回目攻防ループ")   
        #攻撃生成
        attack_payloads = attack.generate_payload(logs,ai_model)
        print(attack_payloads)
        #攻撃
        attack.payload_p(attack_payloads)
        
if __name__ == "__main__":
    simulation()
