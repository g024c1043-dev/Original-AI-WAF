import requests
import json


# res = requests.get("http://localhost:3000/api/Challenges")
# for c in res.json()["data"]:
#     print(c)

# Juice shopのチャレンジの中から特定のチャレンジを探索
def api_solved():
    res = requests.get("http://localhost:3000/api/Challenges")
    solved_list = []
    for i in res.json()["data"]:
        if i["solved"] == True:
            solved_list.append([i["id"],i["key"],i["name"],i["description"],i["difficulty"]])

    if solved_list:
        for i in solved_list:
            print(f"攻略済みチャレンジ名：{i}")
        return True
    else:
        print("攻略済みのチャレンジはありません")
        return False

# def judge_solved(solved_judge):
#     if solved_judge == True:
#         print("攻撃が成功しました。")
#         return True
#     else:
#         print("攻撃が失敗しました。")
#         return False