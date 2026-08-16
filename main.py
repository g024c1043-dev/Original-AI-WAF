from Attacker import attack
from Defender import defender
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
              "5：処理の終了")
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
                print("処理を終了します...")
                sys.exit(1)
            case _:
                print("エラーが起きました、処理を終了します...")
                sys.exit(1)

if __name__ == "__main__":
    simulation()
