from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from db_utils import save_csv_to_db, run_sql_query, get_table_schema
from llm_engine import generate_sql_query

import os
import traceback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    try:
        print("📥 File received:", file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        db_path = os.path.join(UPLOAD_FOLDER, "data.db")
        table_name = "uploaded_table"

        with open(file_path, "wb") as f:
            f.write(await file.read())

        preview = save_csv_to_db(file_path, db_path, table_name)
        print("✅ Preview generated")
        schema = get_table_schema(db_path, table_name)
        columns = schema.split(", ")
        return {"preview": preview, "schema": schema}

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.post("/query")
async def query_data(question: str = Form(...)):
    try:
        db_path = os.path.join(UPLOAD_FOLDER, "data.db")
        table_name = "uploaded_table"
        schema = get_table_schema(db_path, table_name)
        columns = schema.split(", ")

        schema_context = f"Table name: {table_name}, Columns: {schema}"

        sql = generate_sql_query(question, schema_context, table_name, columns)
        result = run_sql_query(db_path, sql)
        return {"sql": sql, "results": result}

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=400, content={"error": str(e)})