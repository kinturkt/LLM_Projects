import os
from dotenv import load_dotenv
from supabase import create_client
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

# ─── Setup ──────────────────────────────────────
load_dotenv()

sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
emb = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Initialize LLM for generating answers
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.1
)

def ask_single_question(question: str):
    """Ask one specific question and get a direct answer with source."""
    print(f"❓ Question: {question}")
    print("🔍 Searching...")
    
    # Generate embedding for the question
    query_vector = emb.embed_query(question)
    
    # Search for the most relevant content
    response = sb.rpc('search_press_releases', {
        'query_embedding': query_vector,
        'similarity_threshold': 0.1,
        'match_count': 3  # Get top 3 most relevant chunks
    }).execute()
    
    if not response.data:
        print("❌ No relevant information found.")
        return
    
    # Get the best match
    best_match = response.data[0]
    similarity_score = best_match['similarity']
    source_url = best_match['source_url']
    
    # Combine top chunks for context
    context = "\n\n".join([chunk['content'] for chunk in response.data])
    
    # Generate a direct answer
    prompt = f"""
    Based on the following press release information, answer the question directly and concisely.
    
    Context from Prologis Press Release:
    {context}
    
    Question: {question}
    
    Provide a specific, factual answer. If the exact information isn't available, say so.
    """
    
    try:
        answer = llm.invoke(prompt).content
        
        # Display the result
        print("\n" + "="*70)
        print("📋 ANSWER")
        print("="*70)
        print(f"\n💡 ANSWER: {answer}")
        print(f"\n🎯 SIMILARITY SCORE: {similarity_score:.3f}")
        print(f"\n🔗 SOURCE URL: {source_url}")
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"❌ Error generating answer: {e}")

if __name__ == "__main__":
    # Your specific question
    question = "What was the dividend announced in December 2024?"
    
    ask_single_question(question)