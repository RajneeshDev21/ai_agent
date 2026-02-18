import boto3
import json
import requests

from awsBedrockClient.AwsBedrockClient import bedrock_agent_runtime_client


class ResearchAssistantAgent:
    def __init__(self, bedrock_client):
        self.bedrock = bedrock_client  # Amazon Bedrock client
        self.memory = []  # Memory to store conversation history and context
        self.tools = {
            "search_web": self.search_web,
            "summarize": self.summarize_text
        }

    def invoke_mistral(self, prompt, max_tokens=100):
        """Invoke the Mistral model via Amazon Bedrock."""
        model_id = "mistral-7b"  # Replace with the actual Mistral model ID
        request_body = {
            "prompt": prompt,
            "max_tokens": max_tokens
        }
        response = self.bedrock.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )
        response_body = json.loads(response["body"].read())
        return response_body.get("completion", "")

    def search_web(self, query):
        """Tool to perform a web search using an external API."""
        url = "https://api.searchengine.com/search"
        params = {"q": query, "api_key": "your_search_api_key"}
        response = requests.get(url, params=params)
        return response.json().get("results", [])

    def summarize_text(self, text):
        """Tool to summarize long text using Mistral."""
        prompt = f"Summarize the following text in 2-3 sentences:\n{text}"
        return self.invoke_mistral(prompt)

    def plan_and_execute(self, user_query):
        """Plan and execute actions to answer the user's query."""
        self.memory.append(f"User Query: {user_query}")

        # Step 1: Generate a plan using Mistral
        planning_prompt = f"""
        You are a research assistant. Your task is to answer the following question:
        "{user_query}"
        Plan the steps you need to take. You have access to the following tools:
        - search_web(query): Searches the web for information related to the query.
        - summarize(text): Summarizes long text into a concise summary.
        """
        plan = self.invoke_mistral(planning_prompt)
        self.memory.append(f"Plan: {plan}")

        # Step 2: Execute the plan
        if "search_web" in plan:
            search_query = plan.split("search_web(")[1].split(")")[0].strip('"')
            search_results = self.tools["search_web"](search_query)
            self.memory.append(f"Search Results: {search_results}")

            # Extract relevant information from search results
            relevant_info = "\n".join([result["snippet"] for result in search_results[:3]])

            # Summarize the relevant information
            summary = self.tools["summarize"](relevant_info)
            self.memory.append(f"Summary: {summary}")
            return summary

        elif "summarize" in plan:
            text_to_summarize = plan.split("summarize(")[1].split(")")[0].strip('"')
            summary = self.tools["summarize"](text_to_summarize)
            self.memory.append(f"Summary: {summary}")
            return summary

        else:
            return "I'm sorry, I couldn't find a way to answer your question."


# Example usage
if __name__ == "__main__":
    # Initialize the Bedrock client
    # bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")  # Replace with your region
    bedrock = bedrock_agent_runtime_client()
    # Initialize the Research Assistant Agent
    agent = ResearchAssistantAgent(bedrock)

    # User query
    user_query = "What are the latest advancements in quantum computing?"

    # Get the agent's response
    response = agent.plan_and_execute(user_query)
    print(response)
