import json
import pandas as pd

from ai_agent_v2.query_agent_generate_query_1 import question, sql_V1, db_schema
from awsBedrockClient.AwsBedrockClient import bedrock_client, call_mistral
from awsBedrockClient.PgGraphDBConnection import get_pg_graph_db

MODEL_ID = "mistral.mistral-large-2402-v1:0"
client = bedrock_client()
db = get_pg_graph_db()

def refine_sql_external_feedback(
        question: str,
        sql_query: str,
        df_feedback,
        schema: str,
        model: str,
) -> tuple[str, str]:
    """
    Evaluate whether the SQL result answers the user's question and,
    if necessary, propose a refined version of the query.
    Returns (feedback, refined_sql).
    """

    if isinstance(df_feedback, pd.DataFrame):
        sql_output = df_feedback.to_markdown(index=False)
    else:
        sql_output = str(df_feedback)

    prompt = f"""
    You are a SQL reviewer and refiner.

    User asked:
    {question}

    Original SQL:
    {sql_query}

    SQL Output:
    {sql_output}

    Table Schema:
    {schema}

    Step 1: Briefly evaluate if the SQL output answers the user's question.
    Step 2: If the SQL could be improved, provide a refined SQL query.
    If the original SQL is already correct, return it unchanged.

    Return a strict JSON object with two fields:
    - "feedback": brief evaluation and suggestions
    - "refined_sql": the final SQL to run
    """

    content = call_mistral(client, prompt, MODEL_ID)
    try:
        obj = json.loads(content)
        feedback = str(obj.get("feedback", "")).strip()
        refined_sql = str(obj.get("refined_sql", sql_query)).strip()
        if not refined_sql:
            refined_sql = sql_query
    except Exception:
        # Fallback if the model does not return valid JSON:
        # use the raw content as feedback and keep the original SQL
        feedback = content.strip()
        refined_sql = sql_query

    return feedback, refined_sql


# Example: Refine SQL with External Feedback (V1 → V2)

# Execute the original SQL (V1)
df_sql_V1 = db.run(sql_V1)

# Use external feedback to evaluate and refine
feedback, sql_V2 = refine_sql_external_feedback(
    question=question,
    sql_query=sql_V1,   # V1 query
    df_feedback=df_sql_V1,    # Output of V1
    schema=db_schema,
    model="openai:gpt-4.1"
)

# --- V1 ---
print("User Question.....",question)

print("Generated SQL Query (V1).....",sql_V1)

print("SQL Output of V1 - ❌ Does NOT fully answer the question.....",df_sql_V1)

# --- Feedback & V2 ---
print("Feedback on V1.....",feedback)
print("Refined SQL Query (V2).....",sql_V2)

# Execute and display V2 results
df_sql_V2 = db.run(sql_V2)

print("SQL Output of V2 (with External Feedback) - ✅ Fully answers the question....",df_sql_V2)
