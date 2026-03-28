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

# Automatically initialize DB with new columns if it doesn't exist
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, song_name TEXT, 
        overall_score REAL, pitch_score REAL, rhythm_score REAL, 
        pitch_feedback TEXT, rhythm_feedback TEXT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id))''')
    conn.commit()
    conn.close()

init_db()

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
    with open("index.html", "r", encoding="utf-8") as f: return f.read()

@app.get("/auth", response_class=HTMLResponse)
async def serve_auth():
    with open("auth.html", "r", encoding="utf-8") as f: return f.read()

# --- NEW ROUTE FOR DASHBOARD ---
@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    with open("dashboard.html", "r", encoding="utf-8") as f: return f.read()

@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    user = query_db("SELECT * FROM users WHERE username = ?", [username], one=True)
    if user: raise HTTPException(status_code=400, detail="Username already exists")
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
    if not user: raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"status": "success", "user_id": user["id"], "username": user["username"]}

@app.post("/rename-song")
async def rename_song(
    user_id: int = Form(...), 
    old_name: str = Form(...), 
    new_name: str = Form(...)
):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        UPDATE history 
        SET song_name = ? 
        WHERE user_id = ? AND song_name = ?
    ''', (new_name, user_id, old_name))
    conn.commit()
    conn.close()
    
    return {"status": "success"}

@app.post("/validate")
async def validate_singing(user_id: int = Form(...), song_name: str = Form(...), original_file: UploadFile = File(...), user_file: UploadFile = File(...)):
    orig_path = os.path.join(UPLOAD_DIR, original_file.filename)
    user_path = os.path.join(UPLOAD_DIR, user_file.filename)
    with open(orig_path, "wb") as buffer: shutil.copyfileobj(original_file.file, buffer)
    with open(user_path, "wb") as buffer: shutil.copyfileobj(user_file.file, buffer)

    report = analyze_audio(orig_path, user_path)

    if report.get("status") == "success":
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        # Save the raw pitch and rhythm scores now!
        cur.execute('''INSERT INTO history (user_id, song_name, overall_score, pitch_score, rhythm_score, pitch_feedback, rhythm_feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?)''', 
            (user_id, song_name, report["overall_score"], report.get("pitch_score", 0), report.get("rhythm_score", 0), report["pitch_feedback"], report["rhythm_feedback"]))
        conn.commit()
        conn.close()

    os.remove(orig_path)
    os.remove(user_path)
    return report

# --- NEW API ROUTE TO FETCH DATA FOR THE CHART ---
@app.get("/api/history/{user_id}")
async def get_history(user_id: int):
    history = query_db("SELECT * FROM history WHERE user_id = ? ORDER BY date ASC", [user_id])
    return {"status": "success", "data": [dict(row) for row in history]}

@app.get("/api/user-songs/{user_id}")
async def get_user_songs(user_id: int):
    # Fetch DISTINCT (unique) song names for this specific user
    songs = query_db("SELECT DISTINCT song_name FROM history WHERE user_id = ?", [user_id])
    
    # Return them as a simple list of strings
    return {"status": "success", "data": [row["song_name"] for row in songs]}