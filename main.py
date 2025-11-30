import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from openai import OpenAI

# --- BAGIAN 1: Fix Error Dotenv ---
# Kita pakai try-except agar di Local jalan, di Leapcell tidak error
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Di Leapcell library ini tidak ada, jadi kita skip saja (aman)

# --- Konfigurasi ---
app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Setup OpenAI
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Database Sederhana
fake_db = []

# --- Models ---


class JournalItem(BaseModel):
    content: str

# --- Helper AI ---


def get_ai_summary(text: str):
    if not api_key:
        return "Error: API Key OpenAI belum diset."
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize this journal entry into one single concise sentence."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Gagal: {str(e)}"

# --- ROUTES ---

# --- BAGIAN 2: Fix Health Check Leapcell (PENTING!) ---


@app.get("/kaithhealthcheck")
async def health_check():
    # Ini membuat Leapcell senang dan tidak memutus koneksi
    return {"status": "ok"}


@app.head("/kaithhealthcheck")
async def health_check_head():
    return {"status": "ok"}

# --- Route Utama ---


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "journals": fake_db})


@app.post("/api/journals")
async def create_journal(item: JournalItem):
    summary = get_ai_summary(item.content)
    new_entry = {
        "id": len(fake_db) + 1,
        "content": item.content,
        "summary": summary
    }
    fake_db.insert(0, new_entry)
    return new_entry


@app.delete("/api/journals/{journal_id}")
async def delete_journal(journal_id: int):
    global fake_db
    fake_db = [j for j in fake_db if j["id"] != journal_id]
    return {"message": "Deleted"}
