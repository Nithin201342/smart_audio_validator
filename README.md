# SingSmart (Smart Audio Validator)

> An AI-powered web application for analyzing, grading, and improving vocal performances using advanced audio processing.

## Overview

Designed as a final MCA project, this application uses advanced Digital Signal Processing (DSP) and Dynamic Time Warping (DTW) to mathematically compare a user's singing performance against a professional ground-truth reference track. It provides instant feedback on pitch accuracy, rhythmic timing, and tracks user progress over time via a dynamic dashboard.

## Features

- **Advanced Audio Analysis:** Extracts chroma features (pitch) and onset strength (rhythm) using `librosa` to calculate highly accurate error scores.
- **Trouble Spot Locator:** Pinpoints the exact millisecond of the user's biggest mistake for targeted practice.
- **Interactive Dashboard:** Tracks user accuracy over time with song-specific filters using `Chart.js`.
- **Dual Visualizers:** Real-time audio waveform rendering powered by `Wavesurfer.js`.
- **Secure Authentication:** SQLite-backed user registration and login system.

## Repository Structure

- `main.py` — FastAPI application entry point and database routing.
- `audio_processor.py` — Core AI logic, DTW algorithms, and Librosa processing.
- `database.py` — SQLite initialization script.
- `index.html` — Main workspace and audio visualizer UI.
- `dashboard.html` — User progress charts and AI weakness analysis.
- `auth.html` — Secure login and registration UI.
- `audio_samples/` — Reference tracks for testing the application.

## Requirements

This project targets Python 3.8+. It is highly recommended to use a virtual environment.

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.\.venv\Scripts\Activate.ps1   # Windows

# 2. Install dependencies
pip install -r requirements.txt

# Running the App
Initialize the database (Run this once to create the SQLite tables):
python database.py

Start the ASGI Server:
uvicorn main:app --reload

After the server starts, open your browser and navigate to http://127.0.0.1:8000.

Tech Stack
Backend: Python, FastAPI, Librosa, NumPy, SQLite

Frontend: HTML/CSS/JS, Wavesurfer.js, Chart.js, Vanta.js


This version is punchy, highly professional, and accurately reflects the impressive engineering you did. 

Once you push this to GitHub, your project is completely done! How are you feeling abo