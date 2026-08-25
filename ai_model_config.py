import os
import sys

def get_ai_model(use_model):
    match use_model:
        case "1":
            return {
                "api_key": "not_needed",
                "base_url": "http://localhost:1234/v1",
                "model": "google/gemma-4-12b-qat",
            }
        case "2":
            return {
                "api_key": os.environ["Groq_API_KEY"],
                "base_url": "https://api.groq.com/openai/v1",
                "model": "openai/gpt-oss-20b",
            }
        case "3":
            return {
                "api_key": "not_needed",
                "base_url": "http://localhost:1234/v1",
                "model": "lily-cybersecurity-7b-v0.2",
            }
        case "4":
            return {
                "api_key": "not_needed",
                "base_url": "http://localhost:1234/v1",
                "model": "llama-3-whiterabbitneo-8b-v2.0",
            }
        case _:
            print("クライアント取得に失敗したため処理を終了します...")
            sys.exit()