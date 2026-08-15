from Attacker import attack
from Defender import defender
import sys

def simulation():
    attacker_response = None
    while True:
        print("1：攻撃側操作\n"
              "2：防御側操作\n"
              "3：WAF操作\n"
              "4：処理の終了")
        user_action = input("操作を選択してください:")
        match user_action:
            case "1":
                #attack.pyに攻撃とペイロードを生成させる
                attacker_response = attack.main(attacker_response)
            case "2":
                defender_response = defender.main()
            case "3":
                print("未実装")
            case "4":
                print("処理を終了します...")
                sys.exit(1)
            case _:
                print("エラーが起きました、処理を終了します...")
                sys.exit(1)
        
       
    

if __name__ == "__main__":
    simulation()
