def choice_ai_model():
    while True:
        print("1:ローカルAI\n"
              "2:クラウドAI\n")
        ai_model=input("使用するAI環境を選択してください：")
        if ai_model == "1":
            print("1：google/gemma-4-12b-qat\n"
                  "2：lily-cybersecurity-7b-v0.2\n" \
                  "3：llama-3-whiterabbitneo-8b-v2.0\n")
            ai_model = input("使用するモデルを選択：")
            return ai_model
        
        elif ai_model == "2":
            print("4：openai/gpt-oss-20b\n")
            ai_model = input("使用するモデルを選択：")
            return ai_model
        
        else:
            print("表示されている数値のみを入力してください...")