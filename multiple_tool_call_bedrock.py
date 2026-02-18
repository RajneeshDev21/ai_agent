from datetime import datetime
import json
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_aws import ChatBedrock
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from awsBedrockClient.AwsBedrockClient import bedrock_client

llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    client=bedrock_client()
)

@tool
def get_weather_from_ip():
    """Returns current weather based on IP location."""
    return "28°C, Sunny"


@tool
def write_txt_file(content: str, filename: str = "note.txt"):
    """Writes content to a text file."""
    with open(filename, "w") as f:
        f.write(content)
    return f"{filename} written successfully"


@tool
def get_today_date():
    """Returns today's date in YYYY-MM-DD format."""
    return datetime.today().strftime("%Y-%m-%d")

@tool
def generate_qr_code(url: str, image_name: str):
    """Generates a QR code for a URL."""
    return f"QR code generated for {url} using {image_name}"

tools = [
    get_today_date,
    generate_qr_code,
    write_txt_file,
    get_weather_from_ip
]

llm_with_tools = llm.bind_tools(tools)

prompt = ("You are an assistant that MUST use tools when they are relevant. If the user asks for the current time, you MUST call the get_today_date tool."
          " If the user asks for the weather, you MUST call the get_weather_from_ip tool. If the user asks to write a note, you MUST call the write_txt_file tool. If the user asks to generate a QR code, you MUST call the generate_qr_code tool.")

input = "Can you get the weather ?"
messages = [
    SystemMessage(
        content=prompt
    ),
    ("user", input)
]

response = llm_with_tools.invoke(messages)
print(json.dumps(response.model_dump(), indent=2, default=str))



