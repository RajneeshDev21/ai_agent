
from datetime import datetime
import json
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_aws import ChatBedrock
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from awsBedrockClient.AwsBedrockClient import bedrock_client
from IPython.display import Image, display

llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    client=bedrock_client()
)

@tool
def get_today_date():
    """Returns today's date in YYYY-MM-DD format."""
    return datetime.today().strftime("%Y-%m-%d")

llm_with_tools = llm.bind_tools([get_today_date])

messages = [
    SystemMessage(
        content=(
            "You are an assistant that MUST use tools when they are relevant. "
            "If the user asks for the current time, you MUST call the get_today_date tool."
        )
    ),
    ("user", "What date today is ?")
]

response = llm_with_tools.invoke(messages)
#print(response)

print(json.dumps(response.model_dump(), indent=2, default=str))


# --------------------
# LLM Setup
# --------------------
llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    client=bedrock_client()
)


# --------------------
# Tool Definition
# --------------------
@tool
def get_today_date():
    """Returns today's date in YYYY-MM-DD format."""
    return datetime.today().strftime("%Y-%m-%d")


llm_with_tools = llm.bind_tools([get_today_date])

# --------------------
# Initial Messages
# --------------------
messages = [
    SystemMessage(
        content=(
            "You are an assistant that MUST use tools when relevant. "
            "If the user asks for today's date, you MUST call get_today_date."
        )
    ),
    HumanMessage(content="What date today is?")
]

# --------------------
# First LLM Call
# --------------------
response = llm_with_tools.invoke(messages)

response2 = None
# --------------------
# Tool Call Handling (Bedrock Version)
# --------------------
if response.tool_calls:
    tool_call = response.tool_calls[0]

    tool_name = tool_call["name"]
    tool_args = tool_call.get("args", {})
    tool_call_id = tool_call["id"]

    # Execute tool locally
    if tool_name == "get_today_date":
        tool_result = get_today_date.invoke(tool_args)

    # Append AI response (with tool call)
    messages.append(response)

    # Append tool result
    messages.append(
        ToolMessage(
            content=str(tool_result),
            tool_call_id=tool_call_id
        )
    )

    # Second LLM call
    response2 = llm_with_tools.invoke(messages)

    print(response2.content)

