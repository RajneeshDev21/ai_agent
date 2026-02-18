
import boto3
import json

from awsBedrockClient.AwsBedrockClient import bedrock_client


def get_weather(city: str) -> str:

    if city == 'delhi':
        return f"Temperature: 24°C, Condition:  clear sky"

    if city == 'mumbai':
        return f"Temperature: 24°C, Condition: clear sky"


bedrock= bedrock_client()

def ai_agent(user_input: str):
    system_prompt = """
                You are an AI agent.
                If the user asks about weather, respond ONLY in JSON like:
                {
                  "action": "get_weather",
                  "city": "<city name>"
                }
                
                Otherwise respond:
                {
                  "action": "final",
                  "answer": "<your answer>"
                }
        """

    body = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        "max_tokens": 200,
        "temperature": 0
    }

    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body=json.dumps(body)
    )

    result = json.loads(response["body"].read())
    content = result["content"][0]["text"]

    return json.loads(content)

def run_agent(user_input):

    decision = ai_agent(user_input)
    print("weather:", decision)
    if decision["action"] == "get_weather":
        weather = get_weather(decision["city"])

        final_answer = f"Weather in {decision['city']}:\n{weather}"
        return final_answer

    return decision["answer"]

if __name__ == "__main__":
    while True:
        #user_input = input("You: ")
        #if user_input.lower() in ("exit", "quit"):
         #   break

        response = run_agent("delhi")
        print("Agent:", response)
