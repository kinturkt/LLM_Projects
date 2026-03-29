# 🤖 LLM Projects

A collection of practical apps built using Large Language Models (LLMs) like Gemini Pro, Groq, and OpenAI. These projects combine FastAPI, Streamlit, and LLM APIs to solve real-world problems using natural language.

---

## 📂 Projects

### ✅ Completed

1. **🧠 Gemini AI Assistant Bot** A conversational assistant powered by Gemini, capable of answering general queries in real time.

2. **📺 YouTube Video Summarizer** Paste a YouTube link and get a concise summary of the video content using LLM-powered transcription and summarization.

3. **📄 Intelligent ATS Resume Analyzer** Upload a resume and job description, get ATS insights, keyword match percentage, and a suitability score.

4. **📊 SQLMind - LLM SQL Data Analyst** Upload any CSV, ask natural-language questions, and get SQL-generated answers with charts and summaries.

5. **🎬 MovieFindr - Recommendation System** A content discovery engine built with Elasticsearch and Pandas to help users find their next favorite film.

---

### 🚧 In Progress

6. **🤖 AgenticAI - Multi-Agent Orchestration System** A complex AI platform utilizing the Model Context Protocol (MCP). Features a Master Agent coordinating specialized sub-agents (SRE, Network, Finance) for enterprise-level task execution.

7. **🧠 DualLLM Summarizer Chat** Upload a document and ask questions, get side-by-side answers from **Gemini** and **Groq** for comparison and deeper insight.

8. **👗 Fashion Product Image Recognition** An AI-powered computer vision application featuring a custom Gradio web UI to classify and recognize various fashion items.

---

### 🔜 Coming Soon

9. **📈 AIViz - Chart Generator from Natural Language** Ask for charts in plain English - generate matplotlib or seaborn plots instantly.

10. **🎙️ TalkWise - Personal AI Voice Assistant** Voice-enabled assistant powered by LLMs - speak naturally, ask questions, and get spoken or visual responses in real time.

---

## 🧰 Tech Stack

- **LLMs**: Gemini 2.5 / Gemini 1.5, Groq, OpenAI (modular & swappable)
- **LLM Orchestration**: LangChain for prompt routing and multi-model pipelines
- **Backend**: FastAPI + Uvicorn
- **Frontend**: Streamlit
- **Database**: SQLite for chat history and file storage
- **Data Analysis**: Pandas
- **Language**: Python
- **Embeddings**: `text-embedding-3-small`, `InstructorXL`
- **Vector Store**: FAISS or ChromaDB (for RAG)

---

## 📂 Repository Structure

Because this repository houses multiple projects, each application lives in its own dedicated directory. Shared dependencies are managed at the root level.

```text
llm_projects/
├── 1) Gemini AI Assistant Bot/
│   └── app.py
├── 2) YouTube Summarizer/
│   └── app.py
├── 3) ATS Resume Analyzer/
│   └── app.py
├── requirements.txt      # Master Python dependencies for all apps
└── .env                  # Local API keys (Not tracked by Git)
```

--- 

## Quick Start Guide (Run Locally)

1. Clone the repository
```
git clone [https://github.com/kinturkt/llm_projects.git](https://github.com/kinturkt/LLM_Projects.git)
cd LLM_Project
```

2. Install dependencies

```
# It is recommended to use Python 3.11 or 3.12
pip install -r requirements.txt
```

3. Set up environment variables
Create a .env file in the root directory and add your API keys:
```
GEMINI_API_KEY="your_google_api_key_here"
```

4. Run an app
Navigate to the specific project folder and launch Streamlit:
```
streamlit run "1) Gemini AI Assistant Bot/app.py"
```

---

## 🌐 Live Demo Links

- 🧠 Gemini AI Assistant Bot → [Live Demo](https://gemini-ai-assistant-bot.streamlit.app/)
- 📺 YouTube Summarizer → [Live Demo](https://huggingface.co/spaces/kinturkt/YT_Summarizer_App)  
- 📄 ATS Resume Analyzer → [Live Demo](https://ats-resume-analyzer-project.streamlit.app/) 
- 📊 SQLMind → *[Live Demo](https://sqlmind-sql-data-analyst.streamlit.app/)

---

## 📧 Contact

For suggestions or collaboration, feel free to connect:  
[LinkedIn](https://linkedin.com/in/kintur-shah) | [GitHub](https://github.com/kinturkt)
