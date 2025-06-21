# 🧠 LLM SQL Data Analyst

An AI-powered data analyst that lets you **upload any CSV** and **ask natural language questions** — it responds with generated SQL and tabular results.

Built with:
- 🐍 FastAPI (Python backend)
- 🎈 Streamlit (frontend UI)
- 🤖 Google Gemini (LLM)
- 🗃️ SQLite (for fast, temporary DB storage)

---

## 🚀 Features

- 📂 Upload your own CSV files
- 💬 Ask questions like:  
  - `"Which country has the highest GDP?"`  
  - `"Top 5 products by sales in 2022"`
- 🧠 Automatically generates SQL using Google Gemini API
- 🪄 No setup — works from browser once deployed

---

## 🌐 Live Demo

[Streamlit Cloud](https://streamlit.io/cloud)

---

## 🛠️ Local Development

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload


### 2. Frontend

```bash
cd frontend
streamlit run app.py

---

🔐 Setup Gemini API

Get your API key from: https://makersuite.google.com/app/apikey
Create a .env in backend/:

'''bash
GEMINI_API_KEY=your_key_here

---

⚠️ Notes for Users
Please ensure uploaded CSVs:
Are UTF-8 or ISO-8859-1 encoded
Have headers in the first row
Are not password protected or zipped
Are ideally under 20MB (for smooth preview)
