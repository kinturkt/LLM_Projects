# Testing the Supabase Connection
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

sb = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

try:
    response = sb.table("properties").select("*").limit(1).execute()
    print("Connection successful!")
    print(f"Sample data: {response.data}")
except Exception as e:
    print(f"Connection failed: {e}")
