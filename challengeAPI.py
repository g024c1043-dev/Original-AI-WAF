import requests
import json

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

