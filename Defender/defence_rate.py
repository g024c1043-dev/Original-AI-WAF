import json

def defence_rate():
    try:
        with open("./Defender/waf_logs.json", "r", encoding="utf-8") as f:
            log_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        log_data = []

    total = len(log_data)
    #ログが空のときの0除算を防ぐ
    if total == 0:
        print("WAFログが空のため防御率を計算できません")
        return 0.0

    block = sum(
        1 for i in log_data
        if i.get("WAF") == "Blocked" and i.get("score", 0) > 40
    )
    return block / total
