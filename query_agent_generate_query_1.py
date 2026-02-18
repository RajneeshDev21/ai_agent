
from awsBedrockClient.AwsBedrockClient import bedrock_client, call_mistral

MODEL_ID = "mistral.mistral-large-2402-v1:0"

client = bedrock_client()

def generate_sql(ques: str, schema: str) -> str:
    prompt = f"""
    You are a SQL assistant. Given the schema and the user's question, write a SQL query for SQLite.

    Schema:
    {schema}

    User question:
    {ques}

    Respond with the SQL only.
    """
    response = call_mistral(client, prompt, MODEL_ID)

    return response


# Example usage of generate_sql

# We provide the schema as a string
db_schema = """
Table name: transactions
id (INTEGER)
product_id (INTEGER)
product_name (TEXT)
brand (TEXT)
category (TEXT)
color (TEXT)
action (TEXT)
qty_delta (INTEGER)
unit_price (REAL)
notes (TEXT)
ts (DATETIME)
"""

# We ask a question about the data in natural language
question = "Which color of product has the highest total sales?"

# Generate the SQL query using the specified model
sql_V1 = generate_sql(question, db_schema)

# Display the generated SQL query
#print("Generated SQL query:\n", sql_V1)