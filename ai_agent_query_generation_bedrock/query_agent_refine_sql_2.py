import json

from ai_agent_v2.query_agent_generate_query_1 import question, db_schema, sql_V1
from awsBedrockClient.AwsBedrockClient import bedrock_client, call_mistral
from awsBedrockClient.PgGraphDBConnection import get_pg_graph_db

from query_agent_generate_query_1 import generate_sql

MODEL_ID = "mistral.mistral-large-2402-v1:0"

db = get_pg_graph_db()

client = bedrock_client()

def refine_sql(
        question: str,
        sql_query: str,
        schema: str,
) -> tuple[str, str]:
    """
    Reflect on whether a query's *shown output* answers the question,
    and propose an improved SQL if needed.
    Returns (feedback, refined_sql).
    """
    prompt = f"""
You are a SQL reviewer and refiner.

User asked:
{question}

Original SQL:
{sql_query}

Table Schema:
{schema}

Step 1: Briefly evaluate if the SQL OUTPUT fully answers the user's question.
Step 2: If improvement is needed, provide a refined SQL query for SQLite.
If the original SQL is already correct, return it unchanged.

Return STRICT JSON with two fields:
{{
  "feedback": "<1-3 sentences explaining the gap or confirming correctness>",
  "refined_sql": "<final SQL to run>"
}}
"""


    content = call_mistral(client, prompt, MODEL_ID)
    try:
        obj = json.loads(content)
        feedback = str(obj.get("feedback", "")).strip()
        refined_sql = str(obj.get("refined_sql", sql_query)).strip()
        if not refined_sql:
            refined_sql = sql_query
    except Exception:
        # Fallback if model doesn't return valid JSON
        feedback = content.strip()
        refined_sql = sql_query

    return feedback, refined_sql


# Example: refine the generated SQL (V1 → V2)

feedback, sql_V2 = refine_sql(
    question=question,
    sql_query=generate_sql(question,db_schema),  # <- comes from generate_sql() (V1)
    schema=db_schema,  # <- we reuse the schema from section 3.1
)

# Display the original prompt
print("User Question.....",question)

# --- V1 ---
print("Generated SQL Query (V1).....",sql_V1)

# Execute and show V1 output
df_sql_V1 = db.run(sql_V1)

print("SQL Output of V1 - ❌ Does NOT fully answer the question.....",df_sql_V1)


# --- Feedback + V2 ---
print("Feedback on V1.....", feedback)
print("Refined SQL Query (V2).....", sql_V2)

# Execute and show V2 output
df_sql_V2 = db.run(sql_V2)
print("SQL Output of V2 - ❌ Does NOT fully answer the question.....", df_sql_V2)
