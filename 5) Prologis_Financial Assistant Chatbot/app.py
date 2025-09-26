import asyncio
# Ensure an event loop exists for gRPC asyncio clients
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
# from google.oauth2 import service_account
# import vertexai

# Import the SQL agent
from agent_files.sql_agent import generate_sql_response

load_dotenv()

print("Starting Prologis Financial Assistant Chatbot Project....")

@st.cache_resource
def init_clients():
    sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

    # # Load credentials explicitly
    # credentials = service_account.Credentials.from_service_account_file(
    #     os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
    #     scopes=['https://www.googleapis.com/auth/cloud-platform']
    # )
    
    # # Initialize Vertex AI with explicit credentials
    # vertexai.init(
    #     project="ai-financial-agent-467005",
    #     location="us-central1", 
    #     credentials=credentials
    # )

    # 768-dim for press releases
    emb_pr = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    # 1536-dim for SEC reports
    emb_sec = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.1
    )

    return sb, emb_pr, emb_sec, llm

sb, emb_pr, emb_sec, llm = init_clients()

# Search press releases (Source 3) in TOP 4 PAGES
# def search_press_releases(query, limit=15):
#     try:
#         query_vector = emb_pr.embed_query(
#             query,
#             task_type="RETRIEVAL_DOCUMENT"
#         )
#         # Debug statement
#         # print(f"[DEBUG] Query vector type={type(query_vector)}, length={len(query_vector)}")

#         response = sb.rpc('search_press_releases', {       
#             'query_embedding': query_vector,
#             'similarity_threshold': 0.02,
#             'match_count': limit
#         }).execute()
#         return response.data, "press_releases"
#     except Exception as e:
#         st.error(f"Error searching press releases: {str(e)}")
#         return [], "press_releases"

# Search in ALL PAGES

def search_press_releases(query, limit=20):
    try:
        query_vector = emb_pr.embed_query(
            query,
            task_type="RETRIEVAL_DOCUMENT"
        )

        response = sb.rpc("search_all_press_releases",{
            "query_embedding": query_vector,
            "similarity_threshold": 0.02,
            "match_count": limit
            }).execute()
        return response.data, "press_releases"
    except Exception as e:
        st.error(f"Error searching press releases: {str(e)}")
        return [], "press_releases"


# Search SEC reports (Source 1)
def search_sec_reports(query, limit=10):
    try:
        query_vector = emb_sec.embed_query(
            query,
            output_dimensionality=1536,
            task_type="RETRIEVAL_DOCUMENT")

        response = sb.rpc('vector_search', {
            'query_embedding': query_vector,
            'similarity_threshold': 0.02,   
            'match_count': limit
        }).execute()
        # Debug statement
        print(f"[DEBUG] Query vector type={type(query_vector)}, length={len(query_vector)}")

        return response.data, "sec_reports"
    except Exception as e:
        st.error(f"Error searching SEC reports: {str(e)}")
        return [], "sec_reports"


# Search financial and properties tables using SQL agent (Source 2)
def query_structured_data(query):
    try:
        # Use your SQL agent to handle the query
        response = generate_sql_response(query)
        return response, "structured_data"
    except Exception as e:
        st.error(f"Error querying structured data: {str(e)}")
        return "Sorry, I couldn't process your query about financial/property data.", "structured_data"

# Determine intent based on keywords
def determine_intent(query):
    query_lower = query.lower()
    
    # Keywords for each data source
    press_keywords = ['dividend', 'earnings', 'quarter', 'announcement', 'press', 'news', 'declared']
    sec_keywords = ['filing', 'sec', 'annual', 'report', '10-k', '10-q', 'compliance', 'risk']
    financial_keywords = ['revenue', 'profit', 'assets', 'properties', 'property', 'financial', 'income', 'square', 'metro', 'address']
    
    # Score each source
    press_score = sum(1 for keyword in press_keywords if keyword in query_lower)
    sec_score = sum(1 for keyword in sec_keywords if keyword in query_lower)
    financial_score = sum(1 for keyword in financial_keywords if keyword in query_lower)
    
    # Return primary intent
    if press_score >= sec_score and press_score >= financial_score:
        return "press_releases"
    elif sec_score >= financial_score:
        return "sec_reports"
    else:
        return "structured_data"

# Generate answer using LLM with context (for embedding-based sources)
def generate_answer(query, context, source_type):
    prompt = f"""
    You are a helpful financial assistant for Prologis. Answer the user's question based on the provided context.
    
    Context from {source_type}:
    {context}
    
    User Question: {query}
    
    Provide a clear, concise answer in plain English. If the information isn't available in the context, say so.
    """
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Sorry, I encountered an error generating the answer: {str(e)}"

# Streamlit UI 
st.set_page_config(
    page_title="Prologis Financial Assistant Chatbot",
    layout="wide"
)

st.title("Prologis Financial Assistant Chatbot")
st.markdown("Ask questions about Prologis financials, press releases, and SEC reports")

st.markdown("---")
st.markdown(
    "This chat interface is powered by Prologis Financial Assistant Chatbot. "
    "Ask any question about Prologis’s financial and properties metrics, press releases, "
    "or SEC reports, and get a concise, plain-English response."
)

# Sidebar with data source info
with st.sidebar:
    st.header("Data Sources")
    st.markdown("""
    **Source 1:** SEC Reports
    - Annual reports, 10-K, 10-Q filings
    - Embedded and searchable
    
    **Source 2:** Structured Data (SQL Agent)
    - Properties table
    - Financials table
    - Text-to-SQL conversion
    
    **Source 3:** Press Releases
    - Recent company announcements
    - Earnings and dividend news
    - Embedded and searchable
    """)
    st.markdown("---")

# Main chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "source" in message:
            st.caption(f"Intent: {message['intent']}")

# Take user input
if prompt := st.chat_input("Ask about Prologis financials..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process the query
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your question..."):
            # Determine intent
            intent = determine_intent(prompt)
            answer = ""
            source_info = ""

            if intent == "press_releases":
                results, source = search_press_releases(prompt)
                if results:
                    context = "\n\n".join([r['content'] for r in results])
                    source_info = f"Press Releases ({len(results)} articles)"
                    answer = generate_answer(prompt, context, source_info)
                else:
                    answer = "No relevant press releases found."
                    source_info = "Press Releases (no results)"

            elif intent == "sec_reports":
                results, source = search_sec_reports(prompt)
                if results:
                    context = "\n\n".join([r['content'] for r in results])
                    source_info = f"SEC Reports ({len(results)} documents)"
                    answer = generate_answer(prompt, context, source_info)
                else:
                    answer = "No relevant SEC reports found."
                    source_info = "SEC Reports (no results)"

            else:
                answer, source = query_structured_data(prompt)
                source_info = "Structured Data (SQL Query)"

            st.markdown(answer)
            st.caption(f"**Intent:** {intent}")
            
            # Add to session state
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer,
                "source": source_info,
                "intent": intent
            })

# Only for Google CLoud Run deployment
# import os
# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 8501))  # fallback to 8501 if not set
#     import streamlit.web.cli as stcli
#     import sys
#     sys.argv = ["streamlit", "run", "app.py", "--server.port", str(port), "--server.address", "0.0.0.0"]
#     sys.exit(stcli.main())