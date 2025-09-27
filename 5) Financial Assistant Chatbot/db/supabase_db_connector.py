import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Please set DATABASE_URL in your .env to your Supabase Postgres connection string.")

def run_sql_query(query: str):
    """
    Connect to Postgres at DATABASE_URL, run the SQL, return list[dict] or status dict.
    """
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        with conn:
            with conn.cursor() as cur:
                cur.execute(query)
                if cur.description:
                    cols = [c.name for c in cur.description]
                    rows = cur.fetchall()
                    return [dict(zip(cols, row)) for row in rows]
                else:
                    return {"status": "query executed successfully"}
    except Exception as e:
        return {"error": str(e)}
