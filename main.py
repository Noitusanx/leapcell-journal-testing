import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from openai import OpenAI

# --- Setup Dotenv Aman ---
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Setup OpenAI
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
fake_db = []


class JournalItem(BaseModel):
    content: str


def get_ai_summary(text: str):
    if not api_key:
        return "API Key belum diset."
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize this journal entry."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- ROUTES ---

# 1. Health Check (Ejaan BENAR)


@app.get("/kaithhealthcheck")
async def health_check():
    return {"status": "ok"}

# 2. Health Check (Ejaan TYPO - Jaga-jaga log aneh tadi)


@app.get("/kaithheathcheck")
async def health_check_typo():
    return {"status": "ok"}

# Support HEAD method juga untuk kedua route


@app.head("/kaithhealthcheck")
async def head_check(): return {"status": "ok"}


@app.head("/kaithheathcheck")
async def head_check_typo(): return {"status": "ok"}

# --- App Utama ---


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "journals": fake_db})


@app.post("/api/journals")
async def create_journal(item: JournalItem):
    summary = get_ai_summary(item.content)
    new_entry = {"id": len(fake_db)+1,
                 "content": item.content, "summary": summary}
    fake_db.insert(0, new_entry)
    return new_entry


@app.delete("/api/journals/{journal_id}")
async def delete_journal(journal_id: int):
    global fake_db
    fake_db = [j for j in fake_db if j["id"] != journal_id]
    return {"message": "Deleted"}
