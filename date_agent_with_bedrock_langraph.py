import boto3
import json
from datetime import datetime

# Create Bedrock runtime client
bedrock = boto3.client("bedrock-runtime", region_name="us-west-2")

MODEL_ID = "mistral.mistral-large-2402-v1:0"

def get_current_time():
    """Returns the current time as a string."""
    return datetime.now().strftime("%H:%M:%S")


# Define tool configuration (Bedrock format)
tool_config = {
    "tools": [
        {
            "toolSpec": {
                "name": "get_current_time",
                "description": "Returns the current system time",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        }
    ]
}

# User message
messages = [
    {
        "role": "user",
        "content": [{"text": "What time is it?"}]
    }
]

# First call to model
response = bedrock.converse(
    modelId=MODEL_ID,
    messages=messages,
    toolConfig=tool_config
)

output_message = response["output"]["message"]

# Check if model wants to call tool
if "toolUse" in output_message["content"][0]:
    tool_request = output_message["content"][0]["toolUse"]
    tool_name = tool_request["name"]
    tool_use_id = tool_request["toolUseId"]

    # Execute local function
    if tool_name == "get_current_time":
        tool_result = get_current_time()

    # Send tool result back to model
    tool_response = bedrock.converse(
        modelId=MODEL_ID,
        messages=messages + [
            output_message,
            {
                "role": "user",
                "content": [
                    {
                        "toolResult": {
                            "toolUseId": tool_use_id,
                            "content": [{"text": tool_result}]
                        }
                    }
                ]
            }
        ]
    )

    final_answer = tool_response["output"]["message"]["content"][0]["text"]
else:
    final_answer = output_message["content"][0]["text"]

print(final_answer)
