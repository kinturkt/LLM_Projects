import sqlite3
import pandas as pd

def save_csv_to_db(csv_path: str, db_path: str, table_name: str) -> list:
    df = pd.read_csv(csv_path)
    df.columns = [c.strip().replace(" ", "_").lower() for c in df.columns]

    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    preview = df.head(10).to_dict(orient='records')
    conn.close()
    return preview

def get_table_schema(db_path: str, table_name: str) -> str:
    conn = sqlite3.connect(db_path)
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    schema = ", ".join([row[1] for row in cursor.fetchall()])
    conn.close()
    return schema

def run_sql_query(db_path: str, sql: str) -> list:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]