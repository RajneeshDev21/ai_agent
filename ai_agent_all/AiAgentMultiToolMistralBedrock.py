from datetime import datetime
from awsBedrockClient.AwsBedrockClient import bedrock_client

client = bedrock_client()

MODEL_ID = "mistral.mistral-large-2402-v1:0"

# ------------------ TOOLS ------------------

def get_today_date():
    return datetime.today().strftime("%Y-%m-%d")

def get_weather(city):
    return f"The weather in {city} is sunny (demo data)."

def add_numbers(a, b):
    return a + b


# ------------------ TOOL CONFIG ------------------

TOOL_CONFIG = {
    "tools": [
        {
            "toolSpec": {
                "name": "get_today_date",
                "description": "Get today's date",
                "inputSchema": {"json": {"type": "object", "properties": {}}}
            }
        },
        {
            "toolSpec": {
                "name": "get_weather",
                "description": "Get weather for a city",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string"}
                        },
                        "required": ["city"]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "add_numbers",
                "description": "Add two numbers",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "a": {"type": "number"},
                            "b": {"type": "number"}
                        },
                        "required": ["a", "b"]
                    }
                }
            }
        }
    ],
    "toolChoice": {"auto": {}}
}


# ------------------ MAIN CHAT FUNCTION ------------------

def chat(messages):
    print("messages :", messages)
    return client.converse(
        modelId=MODEL_ID,
        messages=messages,
        toolConfig=TOOL_CONFIG,
        inferenceConfig={"maxTokens": 300, "temperature": 0.4}
    )


# ------------------ TOOL EXECUTION HANDLER ------------------

def run_tool(tool_call):
    name = tool_call["name"]
    args = tool_call.get("input", {})

    if name == "get_today_date":
        return get_today_date()

    if name == "get_weather":
        return get_weather(args["city"])

    if name == "add_numbers":
        return add_numbers(args["a"], args["b"])

    return "Unknown tool"


# ------------------ CONVERSATION LOOP ------------------

def chat_with_ai(user_input, history):
    history.append({"role": "user", "content": [{"text": user_input}]})
    response = chat(history)
    print("response :", response)
    message = response["output"]["message"]

    # TOOL CALL DETECTED
    for item in message["content"]:

        if "toolUse" in item:
            tool = item["toolUse"]
            tool_result = run_tool(tool)

            # Append assistant tool call
            history.append(message)

            # Append tool response
            history.append({
                "role": "tool",
                "toolUseId": tool["toolUseId"],
                "content": tool_result
            })
            print("history :", history)
            # Final model response after tool execution
            final = chat(history)
            print("final :", final)
            final_text = final["output"]["message"]["content"][0]["text"]

            print("🤖:", final_text)
            return

    # Normal response
    print("🤖:", message["content"][0]["text"])


# ------------------ DEMO ------------------

chat_history = []

chat_with_ai("What is today's date?", chat_history)
#chat_with_ai("Add 10 and 25", chat_history)
#chat_with_ai("What is the weather in Mumbai?", chat_history)
