import requests

#ブロックルールの生成
block_rule = [
    "' OR 1=1;--",
    "' OR 1=1--",
    " OR 1=1",
]

def waf_req(url,payload):

    email = payload.get("email","")

    for rule in block_rule:
        if rule in email:
            print(f"[WAF]Block:(ルール{rule})")
            return 
        
    print("[WAF]Allowed")
    response = requests.post(url,json=payload)
    return response