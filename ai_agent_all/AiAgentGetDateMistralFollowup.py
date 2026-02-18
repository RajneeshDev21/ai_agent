import requests
from datetime import datetime

from datetime import datetime
import requests
import json

API_KEY = "Lmm2Fh2US5tddtJLaKS6ccyscQEV8mDE"
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"

def get_today_date():
    return datetime.today().strftime("%Y-%m-%d")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_today_date",
            "description": "Get today's date in YYYY-MM-DD format",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


def call_mistral(user_input):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "user", "content": user_input}
        ],
        "tools": tools,
        "tool_choice": "auto"
    }

    response = requests.post(MISTRAL_URL, headers=headers, json=payload)
    return response.json()


def process_user_input(user_input):
    # 1️⃣ First call
    messages = [{"role": "user", "content": user_input}]
    response = call_mistral(user_input)
    print("Initial response:", response)

    message = response["choices"][0]["message"]


    # 2️⃣ If model requests a tool
    if message.get("tool_calls"):
        tool_call = message["tool_calls"][0]

        if tool_call["function"]["name"] == "get_today_date":
            tool_result = get_today_date()

            # 3️⃣ Send tool result back to Mistral
            messages.append(message)  # assistant tool call
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": tool_result
            })
            print("messages......:", messages)

            # 4️⃣ Follow-up call for final answer
            followup = call_mistral(messages)
            print("Follow-up response:", followup["detail"][0]["input"])
            return followup["detail"][0]

    # 5️⃣ Normal response (no tool)
    return message.get("content", "")


# 🔹 Examples
print(process_user_input("What is today's date?"))
#print(process_user_input("Explain PostgreSQL indexes"))