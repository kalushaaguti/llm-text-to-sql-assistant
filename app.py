import os
import sqlite3
import csv
import io
from pathlib import Path

from openai import OpenAI
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# ----------------------------
# Paths (works locally + Render)
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "ai_analytics.db"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# ----------------------------
# OpenAI client (Render uses env vars, not .env)
# ----------------------------
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

# ----------------------------
# FastAPI app
# ----------------------------
app = FastAPI()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Only mount static if the folder exists
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class QuestionIn(BaseModel):
    question: str


def is_safe_sql(sql: str) -> bool:
    """
    Basic safety: only allow SELECT queries.
    Blocks INSERT/UPDATE/DELETE/DROP/ALTER/CREATE/ATTACH/PRAGMA, etc.
    """
    s = sql.strip().lower()
    if not s.startswith("select"):
        return False
    banned = ["insert", "update", "delete", "drop", "alter", "create", "attach", "pragma"]
    return not any(word in s for word in banned)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    # Make sure index.html is inside /templates folder
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/ask")
def ask(q: QuestionIn):
    question = q.question.strip()

    # If OpenAI key is missing, don't crash the whole server — just return a clear error
    if client is None:
        return {"sql": "", "error": "OPENAI_API_KEY is not set on the server (Render Environment Variables)."}

    prompt = f"""
You are an expert data analyst.

Convert this business question into a correct SQLite SQL query.

Database tables:
- customers(customer_id, full_name, email)
- orders(order_id, customer_id, order_date)
- order_items(order_item_id, order_id, product_id, quantity)
- products(product_id, product_name, price)

Rules:
- Only generate a single SQLite SELECT query.
- Do NOT use INSERT/UPDATE/DELETE/DROP/ALTER/CREATE/PRAGMA.
- Return ONLY SQL.

Question: {question}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        sql = response.choices[0].message.content.strip()
        sql = sql.replace("```sql", "").replace("```", "").strip()

        if not is_safe_sql(sql):
            return {"sql": sql, "error": "Blocked unsafe SQL (only SELECT is allowed)."}

        if not DB_PATH.exists():
            return {"sql": sql, "error": f"Database not found at: {DB_PATH}"}

        # Run query
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [d[0] for d in cur.description] if cur.description else []
        conn.close()

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        if columns:
            writer.writerow(columns)
        writer.writerows(rows)
        csv_text = output.getvalue()

        return {"sql": sql, "columns": columns, "rows": rows, "csv": csv_text}

    except Exception as e:
        return {"sql": "", "error": str(e)}
