from datetime import datetime

from awsBedrockClient.AwsBedrockClient import bedrock_client

client = bedrock_client()

MODEL_ID = "mistral.mistral-large-2402-v1:0"  # Bedrock Mistral model


def get_today_date():
    return datetime.today().strftime("%Y-%m-%d")


TOOL_CONFIG = {
    "tools": [
        {
            "toolSpec": {
                "name": "get_today_date",
                "description": "Returns today's date in YYYY-MM-DD format",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        }
    ],
    "toolChoice": {"auto": {}}
}


def call_ai(user_input):
    result = client.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [{"text": user_input}]
            }
        ],
        toolConfig=TOOL_CONFIG,
        inferenceConfig={
            "maxTokens": 200,
            "temperature": 0.6
        }
    )

    return result


def handle_response(response, user_input):
    message = response["output"]["message"]
    print("Model response:", message)
    messages = [{"role": "user", "content": user_input}]

    # Check for toolUse
    for item in message["content"]:
        if "toolUse" in item:
            tool = item["toolUse"]

            if tool["name"] == "get_today_date":
                tool_result = get_today_date()

                messages.append(message)  # assistant tool call
                messages.append({
                    "role": "tool",
                    "toolUseId": tool["toolUseId"],
                    "content": tool_result
                })
                print("messages......:", messages)

                # 4️⃣ Follow-up call for final answer
                followup = call_ai(messages)

                print("Final answer:", followup)
                return

    # Normal text response
    print("Final answer:", message)


user_query = "What is today's date?"
response = call_ai(user_query)
handle_response(response, user_query)