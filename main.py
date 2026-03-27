from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import sqlite3
from audio_processor import analyze_audio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
DB_NAME = "validator.db"

# Helper for DB
def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/auth", response_class=HTMLResponse)
async def serve_auth():
    with open("auth.html", "r", encoding="utf-8") as f:
        return f.read()

# --- AUTHENTICATION ENDPOINTS ---
@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    user = query_db("SELECT * FROM users WHERE username = ?", [username], one=True)
    if user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    user_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"status": "success", "user_id": user_id, "username": username}

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    user = query_db("SELECT * FROM users WHERE username = ? AND password = ?", [username, password], one=True)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"status": "success", "user_id": user["id"], "username": user["username"]}

# --- CORE APP ENDPOINTS ---
@app.post("/validate")
async def validate_singing(
    user_id: int = Form(...),
    song_name: str = Form(...),
    original_file: UploadFile = File(...), 
    user_file: UploadFile = File(...)
):
    orig_path = os.path.join(UPLOAD_DIR, original_file.filename)
    user_path = os.path.join(UPLOAD_DIR, user_file.filename)

    with open(orig_path, "wb") as buffer:
        shutil.copyfileobj(original_file.file, buffer)
    with open(user_path, "wb") as buffer:
        shutil.copyfileobj(user_file.file, buffer)

    # Run the upgraded AI engine
    report = analyze_audio(orig_path, user_path)

    # Save to Database if successful
    if report.get("status") == "success":
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO history (user_id, song_name, overall_score, pitch_feedback, rhythm_feedback)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, song_name, report["overall_score"], report["pitch_feedback"], report["rhythm_feedback"]))
        conn.commit()
        conn.close()

    os.remove(orig_path)
    os.remove(user_path)

    return report

@app.get("/history/{user_id}")
async def get_history(user_id: int):
    history = query_db("SELECT * FROM history WHERE user_id = ? ORDER BY date ASC", [user_id])
    return {"status": "success", "data": [dict(row) for row in history]}