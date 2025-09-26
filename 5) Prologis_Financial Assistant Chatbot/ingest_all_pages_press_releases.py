import os
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import time

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, GOOGLE_API_KEY]):
    raise ValueError("Missing required environment variables")

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

# Using Google's embedding model (768 dimensions)
emb = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=GOOGLE_API_KEY
)
splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=80)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
BASE = "https://ir.prologis.com"

def fetch_all_release_urls():
    urls = set()
    
    # Try sitemap first
    try:
        r = requests.get(f"{BASE}/sitemap.xml", headers=HEADERS, timeout=10)
        r.raise_for_status()
        
        root = ET.fromstring(r.content)
        # Handle namespaces
        namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        for loc in root.findall(".//ns:loc", namespaces) or root.findall(".//loc"):
            href = loc.text.strip() if loc.text else ""
            if "/press-releases/detail/" in href:
                urls.add(href)
                
    except Exception as e:
        print(f"Sitemap approach failed: {e}")
        print("Falling back to paginated scraping...")
        
        # Fallback: scrape press releases pages
        for page in range(1, 103):
            try:
                if page == 1:
                    page_url = f"{BASE}/press-releases"
                else:
                    page_url = f"{BASE}/press-releases?page={page}"
                
                print(f"Scraping page {page}...")
                r = requests.get(page_url, headers=HEADERS, timeout=10)
                r.raise_for_status()
                
                soup = BeautifulSoup(r.text, "html.parser")
                links = soup.find_all("a", href=re.compile(r"/press-releases/detail/"))
                
                for link in links:
                    href = link.get("href")
                    if href:
                        full_url = href if href.startswith("http") else BASE + href
                        urls.add(full_url)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"⚠️ Error scraping page {page}: {e}")
                continue
    
    return sorted(urls)

def extract_text_content(url: str):
    """Extract text content directly from the press release page."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Extract title
        title_elem = soup.find("h1") or soup.find("title")
        title = title_elem.get_text().strip() if title_elem else "No Title"
        
        # Extract date
        date_elem = (soup.find("time") or 
                    soup.find(class_=re.compile(r"date", re.I)) or
                    soup.find("span", string=re.compile(r"\d{4}-\d{2}-\d{2}|\w+ \d{1,2}, \d{4}")))
        
        published_at = None
        if date_elem:
            date_text = date_elem.get("datetime") or date_elem.get_text()
            try:
                for fmt in ["%Y-%m-%d", "%B %d, %Y", "%b %d, %Y"]:
                    try:
                        published_at = datetime.strptime(date_text.strip(), fmt).date()
                        break
                    except ValueError:
                        continue
            except:
                pass
        
        if not published_at:
            published_at = datetime.now().date()
        
        # Extract main content
        content_selectors = [
            "div.content",
            "div.press-release-content", 
            "article",
            "div.main-content",
            ".content-body"
        ]
        
        content = ""
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                content = content_elem.get_text(separator="\n").strip()
                break
        
        if not content:
            paragraphs = soup.find_all("p")
            content = "\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        return title, published_at, content
        
    except Exception as e:
        print(f"⚠️ Error extracting content from {url}: {e}")
        return None, None, None

def ingest_press_release(url: str):
    """Extract content, chunk it, embed, and store in database."""
    print(f"🔗 Processing: {url}")
    
    title, published_at, content = extract_text_content(url)
    
    if not content:
        print(f"⚠️ No content found for {url}, skipping")
        return
    
    # Split content into chunks
    chunks = splitter.split_text(content)
    
    if not chunks:
        print(f"⚠️ No chunks created for {url}, skipping")
        return
    
    try:
        # Generate embeddings (768 dimensions)
        print(f"  • Generating embeddings for {len(chunks)} chunks...")
        vectors = emb.embed_documents(chunks)
        
        # Prepare records for database
        records = []
        for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
            records.append({
                "source_url": url,
                "published_at": published_at.isoformat() if published_at else None,
                "title": title,
                "chunk_index": i,
                "content": chunk,
                "embedding": vector,  # This will be 768 dimensions
            })
        
        # Insert into database
        res = sb.table("press_releases").insert(records).execute()
        print(f"  ✅ Ingested {len(records)} chunks from {url}")
        
    except Exception as e:
        print(f"  ❌ Error ingesting {url}: {e}")

if __name__ == "__main__":
    print("🚀 Starting press release ingestion...")
    
    all_urls = fetch_all_release_urls()
    print(f"📊 Found {len(all_urls)} press release URLs")
    
    if not all_urls:
        print("❌ No URLs found. Please check the website structure.")
        exit(1)
    
    for i, url in enumerate(all_urls, 1):
        print(f"\n[{i}/{len(all_urls)}] Processing press release...")
        ingest_press_release(url)
        time.sleep(1)
    
    print("\n✅ Completed ingestion of all press releases!")
    print("🚀 Ingestion script finished successfully!")