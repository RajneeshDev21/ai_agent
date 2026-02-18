import json
from awsBedrockClient.AwsBedrockClient import bedrock_client

def get_weather(city: str) -> str:

    if city == 'delhi':
        return "15°C"

    if city == 'mumbai':
        return "20°C"


bedrock= bedrock_client()

tools ={"get_weather": get_weather}

SYSTEM_RPOMPT =('you are an AI Assistant with START, PLAN, ACTION, OBSERVATION and Output State.'
                'Wait for the user prompt and first PLAN using available tools.'
                'After Planning, Take the action with appropriate tools and wait for Observation based on Action.'
                'Once you  get the Observation, Return the AI response based on START prompt and observations.'
                
                'Stringify follow the JSON output format as in examples :'
                
                'Available Tools:'
                'function get_weather(city: str) -> str:'
                'get_weather: Get the weather for a given city. Input should be a city name string. return weather string like 24°C'                
                
                'Example:'
                'START'
                '{"type":"user","user":"What is the sum of weather in delhi and mumbai?"}'
                '{"type":"plan","plan":"I will call the get_weather tool to get the weather in delhi"}'
                '{"type":"action","function":"get_weather","input":"delhi"}'
                '{"type":"observation","observation": "24°C"}'
                '{"type":"plan","plan":"I will call the get_weather tool to get the weather in mumbai"}'
                '{"type":"action","function":"get_weather","input":"mumbai"}'
                '{"type":"observation","observation": "24°C"}'                
                '{"type":"output","output":"The sum of weather in delhi and mumbai is 35°C"}')


user = "What's the weather in delhi?"

messages = [{'role': 'system', 'content': SYSTEM_RPOMPT}]

while True:
    query = "weather in delhi and mumbai";
    q = {'type': 'user', 'user': query}

    messages.push({'role': 'user', 'content': q})

    chat = bedrock.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body=json.dumps({
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7,
        }))

    result = chat.choices[0].message['content']
    messages.push({'role': 'assistant', 'content': result})

    call = json.loads(result)

    if (call.type == "output"):
        print("Final Answer:", call.output)
        break
    elif (call.type == "action"):
        func = tools[call.function]
        observation = func(call.input)
        obs = {type: "observation", observation: observation}
        messages.push({'role': 'developer', 'content': obs})


if __name__ == "__main__":
    response = run_agent("delhi")
    print("Agent:", response)