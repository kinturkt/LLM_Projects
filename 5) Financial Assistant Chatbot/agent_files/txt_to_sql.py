import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def generate_sql_from_prompt(user_question: str) -> str:
    """
    Convert a plain-English question into a raw PostgreSQL SQL query using Google Generative AI.
    """
    try:
        # Use the same API key you're already using for embeddings
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.1
        )

        prompt = f"""
            You are a PostgreSQL expert. Generate ONLY the raw SQL (no explanation or markdown).

            Schema public.properties(
            id BIGINT,
            Property_id BIGINT,
            Property_Name TEXT,
            Property_Address TEXT,
            Metro_Area TEXT,
            "Square_Foot (SF)" NUMERIC,
            Property_Type TEXT
            )

            Schema public.financials(
            id BIGINT,
            Property_id BIGINT,
            Year BIGINT,
            Revenue NUMERIC,
            "Net_Income ($)" NUMERIC
            )

            IMPORTANT: Always use double quotes around column names with spaces or special characters:
            - "Square_Foot (SF)" 
            - "Net_Income ($)"

            Example:
            -- question: List the top 5 properties by revenue in 2023
            SELECT p."Property_Name", f."Revenue"
            FROM public.properties AS p
            JOIN public.financials AS f
                ON p."Property_id" = f."Property_id"
            WHERE f."Year" = 2023
            ORDER BY f."Revenue" DESC
            LIMIT 5;

            Now, generate SQL for the following question.
            -- question: {user_question}
            -- SQL:
            """

        response = llm.invoke(prompt)
        sql = response.content.strip()
        # print("🔍 [DEBUG] Generated SQL:", sql)
        return sql

    except Exception as e:
        err = f"-- ERROR: {str(e)}"
        print("🔍 [DEBUG] SQL generation error:", err)
        return err