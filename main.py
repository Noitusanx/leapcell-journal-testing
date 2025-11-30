import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
from typing import List, Optional
from dotenv import load_dotenv

# --- Konfigurasi ---
load_dotenv()

app = FastAPI()

# Setup Template (Frontend)
templates = Jinja2Templates(directory="templates")


client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

fake_db = []

# --- Models ---


class JournalItem(BaseModel):
    content: str

# --- Helper AI ---


def get_ai_summary(text: str):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Summarize this journal entry into one single concise sentence."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Gagal mendapatkan ringkasan AI."


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
    # Insert ke awal list agar yang terbaru di atas
    fake_db.insert(0, new_entry)
    return new_entry

# 3. API: Delete Journal


@app.delete("/api/journals/{journal_id}")
async def delete_journal(journal_id: int):
    global fake_db
    fake_db = [j for j in fake_db if j["id"] != journal_id]
    return {"message": "Deleted"}
