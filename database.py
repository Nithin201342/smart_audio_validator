import sqlite3
import os

DB_NAME = "validator.db"

def init_db():
    """Initializes the SQLite database with Users and History tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # 2. Create History Table (Links to the user who sang the song)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            song_name TEXT,
            overall_score REAL,
            pitch_feedback TEXT,
            rhythm_feedback TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database '{DB_NAME}' initialized successfully with 'users' and 'history' tables!")

def execute_query(query, params=(), fetchone=False, fetchall=False):
    """Helper function to run database queries easily."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query, params)
    
    data = None
    if fetchone:
        data = cursor.fetchone()
    elif fetchall:
        data = cursor.fetchall()
    else:
        conn.commit()
        
    conn.close()
    return data

if __name__ == "__main__":
    # Run this file directly to create the database
    init_db()