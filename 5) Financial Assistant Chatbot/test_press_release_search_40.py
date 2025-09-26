# test_semantic_search.py

import os
from dotenv import load_dotenv
from supabase import create_client
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# ─── Configuration ──────────────────────────────────────
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, GOOGLE_API_KEY]):
    raise ValueError("Missing required environment variables")

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

# Same embedding model used for ingestion
emb = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=GOOGLE_API_KEY
)

def semantic_search(query: str, limit: int = 5):
    """Perform semantic search on press releases."""
    print(f"🔍 Searching for: '{query}'")
    
    # 1. Generate embedding for the query using the same model
    query_vector = emb.embed_query(query)
    
    # 2. Perform vector similarity search in Supabase
    # Using cosine distance (1 - cosine_similarity)
    response = sb.rpc(
        'match_press_releases_top_4',
        {
            'query_embedding': query_vector,
            'match_threshold': 0.8,  # Similarity threshold
            'match_count': limit
        }
    ).execute()
    
    return response.data

def display_results(results):
    """Display search results in a readable format."""
    if not results:
        print("❌ No results found.")
        return
    
    print(f"\n📊 Found {len(results)} relevant results:")
    print("=" * 80)
    
    for i, result in enumerate(results, 1):
        similarity = 1 - result['similarity']  # Convert distance to similarity
        print(f"\n[{i}] 📰 {result['title']}")
        print(f"📅 Published: {result['published_at']}")
        print(f"🎯 Similarity: {similarity:.3f}")
        print(f"🔗 URL: {result['source_url']}")
        print(f"📝 Content Preview: {result['content'][:200]}...")
        print("-" * 40)

def interactive_search():
    """Interactive search interface."""
    print("🚀 Prologis Press Release Semantic Search")
    print("Type 'quit' to exit")
    print("=" * 50)
    
    while True:
        query = input("\n💬 Enter your search query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not query:
            print("❌ Please enter a valid query.")
            continue
        
        try:
            results = semantic_search(query, limit=5)
            display_results(results)
        except Exception as e:
            print(f"❌ Error during search: {e}")

if __name__ == "__main__":
    # Test with predefined queries first
    test_queries = [
        "quarterly earnings results",
        "dividend announcement",
        "real estate acquisition",
        "financial performance",
        "quarterly dividends"
    ]
    
    print("🧪 Testing with predefined queries...")
    for query in test_queries:
        print(f"\n{'='*60}")
        results = semantic_search(query, limit=3)
        display_results(results)
        print()
    
    # Then start interactive mode
    interactive_search()