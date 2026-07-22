import requests
import json


# res = requests.get("http://localhost:3000/api/Challenges")
# for c in res.json()["data"]:
#     print(c)

# Juice shopのチャレンジの中から特定のチャレンジを探索
def api_solved(challenge_name):
    res = requests.get("http://localhost:3000/api/Challenges")
    for i in res.json()["data"]:
        if i["name"] == challenge_name:
            return i["solved"]
    return False
# def judge_solved(solved_judge):
#     if solved_judge == True:
#         print("攻撃が成功しました。")
#         return True
#     else:
#         print("攻撃が失敗しました。")
#         return False