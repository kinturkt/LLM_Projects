import os
import re
import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, GOOGLE_API_KEY]):
    raise ValueError("Missing one or more required environment variables")

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

emb = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=GOOGLE_API_KEY
)
splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=80)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
BASE = "https://ir.prologis.com"

def fetch_press_release_urls(max_pages=4):
    urls = set()

    for page in range(1, max_pages + 1):
        try:
            if page == 1:
                page_url = f"{BASE}/press-releases"
            else:
                page_url = f"{BASE}/press-releases?page={page}"

            print(f"Scraping page {page}...")
            resp = requests.get(page_url, headers=HEADERS, timeout=10)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.find_all("a", href=re.compile(r"/press-releases/detail/"))

            for link in links:
                href = link.get("href")
                if href:
                    full_url = href if href.startswith("http") else BASE + href
                    urls.add(full_url)

            time.sleep(1)

        except Exception as e:
            print(f"Error scraping page {page}: {e}")

    return sorted(urls)

def extract_press_release_content(url: str):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        title_elem = soup.find("h1") or soup.find("title")
        title = title_elem.get_text().strip() if title_elem else "No Title"

        date_elem = (
            soup.find("time") or
            soup.find(class_=re.compile(r"date", re.I)) or
            soup.find("span", string=re.compile(r"\d{4}-\d{2}-\d{2}|\w+ \d{1,2}, \d{4}"))
        )
        published_at = None
        if date_elem:
            date_text = date_elem.get("datetime") or date_elem.get_text()
            for fmt in ("%Y-%m-%d", "%B %d, %Y", "%b %d, %Y"):
                try:
                    published_at = datetime.strptime(date_text.strip(), fmt).date()
                    break
                except ValueError:
                    continue

        if not published_at:
            published_at = datetime.now().date()

        # Try multiple selectors for main content
        selectors = ["div.content", "div.press-release-content", "article", "div.main-content", ".content-body"]
        content = ""
        for sel in selectors:
            elem = soup.select_one(sel)
            if elem:
                content = elem.get_text(separator="\n").strip()
                break

        # Fallback to all paragraphs if no content found
        if not content:
            paragraphs = soup.find_all("p")
            content = "\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])

        return title, published_at, content

    except Exception as e:
        print(f"Failed to extract content from {url}: {e}")
        return None, None, None

# Process a single press release URL: extract, chunk, embed, and store in Supabase
def ingest_press_release(url: str):
    print(f"Processing {url}")

    title, published_at, content = extract_press_release_content(url)

    if not content:
        print(f"No content at {url}, skipping...")
        return

    chunks = splitter.split_text(content)
    if not chunks:
        print(f"No chunks found for {url}, skipping...")
        return

    try:
        print(f"  • Generating embeddings for {len(chunks)} chunks...")
        vectors = emb.embed_documents(chunks)

        records = []
        for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
            records.append({
                "source_url": url,
                "published_at": published_at.isoformat(),
                "title": title,
                "chunk_index": i,
                "content": chunk,
                "embedding": vector,
            })

        # Fixed: Remove the status_code check
        res = sb.table("press_releases_top_4_pages").insert(records).execute()
        
        # The insert operation will raise an exception if it fails
        # If we reach this line, it means the insertion was successful
        print(f"Successfully ingested {len(records)} chunks for {url}")

    except Exception as e:
        print(f"Error ingesting {url}: {e}")

if __name__ == "__main__":
    print("Starting ingestion for first 4 pages of press releases...")

    urls_to_process = fetch_press_release_urls(max_pages=4)
    print(f"Found {len(urls_to_process)} press release URLs in first 4 pages.")

    for idx, url in enumerate(urls_to_process, 1):
        print(f"\n[{idx}/{len(urls_to_process)}] Ingesting press release...")
        ingest_press_release(url)
        time.sleep(1)  # Polite delay to avoid overloading the server

    print("\nFinished ingestion for first 4 pages.")