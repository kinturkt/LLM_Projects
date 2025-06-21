# 🧠 LLM SQL Data Analyst

An AI-powered data analyst that lets you **upload any CSV** and **ask natural language questions** - it responds with generated SQL and tabular results.

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
- No setup — works from browser once deployed

---

---

## 💬 What Kind of Questions Can You Ask?

This app supports natural language questions that are translated into SQL queries. Here are some examples:

#### 🔍 General Analytics
- What’s the total number of insured children per region?
- Show average runs per match for each batsman.
- What is the highest price among all products?
- Which cars have mileage above 25?

#### 📊 Sorting & Ranking
- Who are the top 5 earners by charges?
- List top 3 batsmen by strike rate.
- Which cars have the highest horsepower?

#### 📌 Filtering
- Show all entries where region is northeast.
- List customers with BMI over 30.
- Which movies were released after 2015?

#### 📈 Aggregations
- What’s the average charges by smoker status?
- Total number of children per region?
- Count the number of products in each category.

#### ⚙️ Any question based on:
- Columns like: `age`, `region`, `bmi`, `charges`, etc.
- Dataset headers dynamically detected upon upload


ℹ️ *Note:* Avoid ambiguous or vague questions. The model relies on accurate column names and well-formed queries.

---

## 🌐 Live Demo

[Streamlit Cloud](https://streamlit.io/cloud)

---

## 🛠️ Local Development

1. Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

2. Frontend

```bash
cd frontend
streamlit run app.py
```

## 🔐 Setup Gemini API

Get your API key from: https://makersuite.google.com/app/apikey <br>
Create a .env file in backend/:

```bash
GEMINI_API_KEY=your_key_here
```


## ⚠️ Notes for Users
Please ensure uploaded CSVs:
Are UTF-8 or ISO-8859-1 encoded
Have headers in the first row
Are not password protected or zipped
Are ideally under 20MB (for smooth preview)


## 🤝 Contributing
Contributions are welcome! Feel free to **fork** this repository and submit a **pull request**. 🚀

## Hosted on Streamlit CLoud
[App]([url](https://llm_sql_data_analyst.streamlit.app))

## 📧 Contact
For any suggestions or feedback, reach out via [LinkedIn](https://www.linkedin.com/in/kintur-shah/) | [Github](https://github.com/kinturkt)
