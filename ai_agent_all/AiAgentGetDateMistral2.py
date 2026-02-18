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
    response = call_mistral(user_input)
    print('response.......',response)
    message = response["choices"][0]["message"]

    # ✅ ALWAYS check first
    if "tool_calls" in message and message["tool_calls"]:
        tool_call = message["tool_calls"][0]

        if tool_call["function"]["name"] == "get_today_date":
            result = get_today_date()
            return result

    # If no tool call, return model text
    return message.get("content", "")

print(process_user_input("What is today's date?"))