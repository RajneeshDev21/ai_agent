from langchain_aws import ChatBedrock
from langchain_core.tools import tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate

from awsBedrockClient.AwsBedrockClient import bedrock_client


@tool
def get_today_date() -> str:
    """Returns today's date"""
    from datetime import datetime
    return datetime.today().strftime("%Y-%m-%d")

llm = ChatBedrock(
    model_id="amazon.titan-text-lite-v1",
    client=bedrock_client()
)

prompt = PromptTemplate.from_template(
    """You are a helpful assistant.

You have access to the following tools:
{tools}

Tool names:
{tool_names}

Question: {input}
{agent_scratchpad}
"""
)

agent = create_react_agent(
    llm=llm,
    tools=[get_today_date],
    prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=[get_today_date],
    verbose=True
)

response = agent_executor.invoke({"input": "What is today's date?"})
print(response["output"])
