import os
import sqlite3
import csv
import io
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel

# --- Load env ---
import os
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is missing. Set it in the deployment environment variables.")

client = OpenAI(api_key=api_key)

DB_PATH = BASE_DIR / "ai_analytics.db"

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Optional static folder
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


class QuestionIn(BaseModel):
    question: str


def is_safe_sql(sql: str) -> bool:
    """
    Simple safety: only allow SELECT queries.
    This blocks INSERT/UPDATE/DELETE/DROP/ALTER/etc.
    """
    s = sql.strip().lower()
    if not s.startswith("select"):
        return False
    banned = ["insert", "update", "delete", "drop", "alter", "create", "attach", "pragma"]
    return not any(word in s for word in banned)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/ask")
def ask(q: QuestionIn):
    question = q.question.strip()

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

        return {
            "sql": sql,
            "columns": columns,
            "rows": rows,
            "csv": csv_text
        }

    except Exception as e:
        return {"sql": "", "error": str(e)}
