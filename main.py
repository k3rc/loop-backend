from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os
from models import Music
from database import init_db, SessionLocal
from schemas import MusicCreate

app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_music(title: str = Form(...), artist: str = Form(...), file: UploadFile = File(...)):
    db = SessionLocal()
    filename = file.filename
    save_path = f"uploads/{filename}"
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    music = Music(title=title, artist=artist, filename=filename)
    db.add(music)
    db.commit()
    db.refresh(music)
    db.close()

    return {"message": "Uploaded successfully", "track_id": music.id}

@app.get("/tracks")
def get_tracks():
    db = SessionLocal()
    tracks = db.query(Music).all()
    db.close()
    return tracks
    
@app.get("/")
def root():
    return {"message": "Loop Backend is live"}
