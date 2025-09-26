import os
import time
from supabase import create_client
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# ── 1. Load environment ─────────────────────────────────────────────────────────
load_dotenv()  # expects SUPABASE_URL, SUPABASE_ANON_KEY, GOOGLE_API_KEY in .env

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not all([SUPABASE_URL, SUPABASE_KEY, GOOGLE_API_KEY]):
    raise ValueError("Missing one of SUPABASE_URL, SUPABASE_ANON_KEY, GOOGLE_API_KEY in .env")

# ── 2. Initialize Supabase + Embedder ────────────────────────────────────────────
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
embedder = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

# ── 3. PDF loader & splitter ────────────────────────────────────────────────────
loader   = PyPDFLoader
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

def clean_text(text: str) -> str:
    return text.replace("\x00", " ").strip()

# Load a PDF, split it into chunks
def process_pdf(path: str) -> list[dict]:
    docs = loader(path).load()
    chunks = []
    for doc in docs:
        for idx, chunk in enumerate(splitter.split_documents([doc])):
            text = clean_text(chunk.page_content)
            if not text:
                continue
            chunks.append({
                "source_file": os.path.basename(path),
                "page":        doc.metadata.get("page"),
                "chunk_index": idx,
                "content":     text
            })
    return chunks

DATA_DIR = "data"
records = []

for fname in os.listdir(DATA_DIR):
    if not fname.lower().endswith(".pdf"):
        continue
    pdf_path = os.path.join(DATA_DIR, fname)
    print(f"Processing {fname}")
    chunks = process_pdf(pdf_path)
    texts  = [c["content"] for c in chunks]

    # 1536-dim embeddings for retrieval
    embs = embedder.embed_documents(
        texts,
        output_dimensionality=1536,
        task_type="RETRIEVAL_DOCUMENT"
    )

    for c, emb in zip(chunks, embs):
        records.append({**c, "embedding": emb})

# ── 5. Upsert in batches of 20 ─────────────────────────────────────────────────
BATCH_SIZE = 20
for i in range(0, len(records), BATCH_SIZE):
    batch = records[i : i + BATCH_SIZE]
    res = supabase.table("sec_reports").upsert(batch).execute()
    status = getattr(res, "status_code", getattr(res, "status", res))
    print(f"  • Upserted batch {i//BATCH_SIZE + 1} ({len(batch)} rows), status {status}")
    time.sleep(0.5)