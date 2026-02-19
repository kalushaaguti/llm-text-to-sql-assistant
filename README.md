LLM-Powered Text-to-SQL Analytics Assistant

A production-style AI analytics assistant that allows users to ask business questions in plain English and automatically generates safe SQL queries to retrieve insights from a SQLite database.

This project demonstrates the intersection of:

Large Language Models (LLMs)

SQL Analytics

FastAPI Web Deployment

Real-world Business Intelligence Workflows

✨ Features

✅ Natural language → SQL query generation using OpenAI GPT models
✅ Executes queries against a structured SQLite analytics database
✅ Web-based interface for non-technical users
✅ Built-in SQL safety guardrails (SELECT-only enforcement)
✅ Displays query results instantly in the browser
✅ Exports query outputs as downloadable CSV
✅ Deployable on cloud platforms (Render, Railway, etc.)

🧠 Example Questions Users Can Ask

“What is the total revenue?”

“Who are the top 5 customers by spending?”

“Which product generated the most revenue?”

“How many orders were placed this month?”

The assistant automatically generates the correct SQL and returns results.

🏗️ Tech Stack
Component	Tool
Backend API	FastAPI
Frontend UI	HTML + JavaScript
Database	SQLite
LLM Provider	OpenAI GPT
Deployment	Render
Environment Management	python-dotenv
📂 Project Structure
llm-text-to-sql-assistant/
│
├── app.py                 # FastAPI backend + LLM logic
├── ai_analytics.db        # SQLite sample business dataset
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html         # Web interface
├── .gitignore             # Ignored files (.env, outputs, etc.)
└── README.md              # Project documentation

⚙️ Setup Instructions (Run Locally)
1. Clone the Repository
git clone https://github.com/kalushaaguti/llm-text-to-sql-assistant.git
cd llm-text-to-sql-assistant

2. Create a Virtual Environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

3. Install Dependencies
pip install -r requirements.txt

4. Add Your OpenAI API Key

Create a .env file in the project root:

OPENAI_API_KEY=your_api_key_here

5. Run the App
uvicorn app:app --reload


Then open:

👉 http://127.0.0.1:8000

🔐 SQL Safety Guardrails

To prevent harmful queries, the assistant enforces:

Only SELECT queries are allowed

Blocks unsafe operations such as:

DROP, DELETE, UPDATE, INSERT, ALTER, PRAGMA


This makes the assistant more suitable for real business environments.

🌍 Deployment

This project is cloud-deployable using Render.

Render Start Command:
uvicorn app:app --host 0.0.0.0 --port $PORT

📌 Use Case & Business Value

This tool enables non-technical teams (sales, marketing, operations) to:

Ask questions in plain English

Get reliable SQL-backed answers instantly

Reduce dependency on data analysts for simple reporting

Improve decision-making speed and accessibility

🚀 Future Improvements

Role-based database access control

Support for multi-table schema discovery

Query explanation + visualization dashboards

Vector database + RAG for better schema grounding

Deployment with authentication and monitoring
