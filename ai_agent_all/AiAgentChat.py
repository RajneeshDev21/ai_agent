
# Import relevant functionality
from langchain_community.chat_models import BedrockChat

import datetime
from awsBedrockClient.AwsBedrockClient import bedrock_client


from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from datetime import datetime

model_id = "amazon.titan-text-lite-v1"


# Create the agent
llm = BedrockChat(
    model_id=model_id,
    client=bedrock_client()
)

# 1. Define the tool
@tool
def get_current_date() -> str:
    """Returns the current date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")

# 2. Create a list of tools for the agent
tools = [get_current_date]

# 3. Define the prompt template for the agent
prompt_template = """
You are a helpful AI assistant. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""

# 4. Initialize your LLM (replace with your chosen LLM)
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4")
# For demonstration, we'll use a placeholder
class MockLLM:
    def invoke(self, prompt):
        if "get_current_date" in prompt:
            return "Action: get_current_date\nAction Input: \nObservation: 2025-09-29\nThought: I now know the final answer\nFinal Answer: The current date is 2025-09-29."
        return "Final Answer: I don't know the answer."
llm = MockLLM()

# 5. Create the agent
agent = create_react_agent(llm, tools, PromptTemplate.from_template(prompt_template))

# 6. Create an AgentExecutor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 7. Invoke the agent with a query
response = agent_executor.invoke({"input": "What is the current date?"})
print(response["output"])
