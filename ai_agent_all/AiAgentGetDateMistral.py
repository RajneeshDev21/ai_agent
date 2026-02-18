import requests
from datetime import datetime

from datetime import datetime
import requests
import json

from awsBedrockClient import MODEL_API_KEY

API_KEY = MODEL_API_KEY.MISTRAL_API_KEY
MISTRAL_URL = MODEL_API_KEY.MISTRAL_URL


def get_today_date():
    return datetime.today().strftime("%Y-%m-%d")


def call_mistral_with_tools(user_input):
    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "user", "content": user_input}
        ],
        "tools": [
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
        ],
        "tool_choice": "auto"
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        MISTRAL_URL,
        headers=headers,
        json=payload
    )

    return response.json()

def ai_agent(user_input):
    response = call_mistral_with_tools(user_input)

    message = response["choices"][0]["message"]
    print("Message from Mistral:", message)

    tool_calls = message.get("tool_calls")

    # Tool execution path
    if tool_calls and len(tool_calls) > 0:
        tool_call = tool_calls[0]
        function_name = tool_call["function"]["name"]

        if function_name == "get_today_date":
            result = get_today_date()

            followup_payload = {
                "model": "mistral-small-latest",
                "messages": [
                    {"role": "user", "content": user_input},
                    message,
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": result
                    }
                ]
            }

            followup_response = requests.post(
                MISTRAL_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json=followup_payload
            )

            return followup_response.json()["choices"][0]["message"]["content"]

    # Normal text response
    return message.get("content")



print(ai_agent("what is date today"))
