import os
from supabase import create_client
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# 1. Init
load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))
embedder = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

# 2. Retrieve function
def retrieve_chunks(query: str, k: int = 5):
    q_emb = embedder.embed_query(query, output_dimensionality=1536)
    resp = supabase.rpc("vector_search", {
        "query_embedding": q_emb,
        "match_count": k
    }).execute()
    return resp.data

# 3. Run a test
if __name__ == "__main__":
    hits = retrieve_chunks("What was Prologis’s total revenue in 2022?", k=5)
    for hit in hits:
        print(f"{hit['similarity']:.3f} → {hit['content'][:200].strip()}…")