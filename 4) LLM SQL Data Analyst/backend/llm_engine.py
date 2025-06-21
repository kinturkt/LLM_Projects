# backend/llm_engine.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_sql_query(question: str, schema: str, table_name: str, columns: list[str]) -> str:
    prompt = f"""
        You are an expert SQL assistant.
        Always use the table name: {table_name}.
        Available columns: {', '.join(columns)}.
        Table schema: {schema}
        Write a valid SQL query that answers:
        "{question}"
        Always include a FROM clause. Always return all columns using SELECT * unless asked otherwise.
        Return only the SQL query — no explanation, no markdown.
    """

    try:
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
        response = model.generate_content(prompt)
        output = response.text.strip()
        output = output.replace("```sql", "").replace("```", "").strip()

        for line in output.splitlines():
            line = line.strip()
            if line.lower().startswith(("select", "with", "insert", "update")):
                if "from" not in line.lower():
                    raise ValueError("LLM output is missing a FROM clause.")
                return line.rstrip(';') + ";"

        raise ValueError("LLM did not return a valid SQL query.")

    except Exception as e:
        raise RuntimeError(f"LLM Error: {str(e)}")