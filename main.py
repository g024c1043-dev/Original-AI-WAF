from Attacker import attack
from Defender import defender
import waf

def simulation():
    #attack.pyに攻撃とペイロードを生成させる
    attacker_response = attack.main()
    return attacker_response

if __name__ == "__main__":
    simulation()
