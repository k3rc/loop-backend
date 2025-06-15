from fastapi import (
    FastAPI, UploadFile, File, Form,
    Depends, HTTPException, status
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import os
import shutil
from typing import List

# ──────────────────────────────────────────────
# DB, модели и схемы
# ──────────────────────────────────────────────
from database import Base, engine, get_db          # Base & get_db из database.py
from models import Track                           # ORM‑модель
from schemas import TrackOut                       # Pydantic‑схема
from auth import verify_token                      # проверка Telegram‑токена
from sqlalchemy.orm import Session

# Создать таблицы, если их ещё нет
Base.metadata.create_all(bind=engine)

# ──────────────────────────────────────────────
# APP и CORS
# ──────────────────────────────────────────────
app = FastAPI(title="Loop Backend")

origins = [
    "https://loop-frontend-three.vercel.app",
    "http://localhost:3000",          # удобно для локальной отладки
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Статическая раздача загруженных файлов
# ──────────────────────────────────────────────
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ──────────────────────────────────────────────
# Роут: загрузка трека
# ──────────────────────────────────────────────
@app.post("/upload", response_model=TrackOut, status_code=status.HTTP_201_CREATED)
async def upload_track(
    title:  str        = Form(...),
    artist: str        = Form(...),
    album:  str        = Form(...),
    genre:  str        = Form(...),
    file:   UploadFile = File(...),
    cover:  UploadFile = File(...),
    token:  str        = Form(...),
    db: Session        = Depends(get_db),
):
    # 1) авторизация
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # 2) сохранение файлов
    audio_path = os.path.join(UPLOAD_DIR, file.filename)
    cover_path = os.path.join(UPLOAD_DIR, cover.filename)

    with open(audio_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    with open(cover_path, "wb") as f:
        shutil.copyfileobj(cover.file, f)

    # 3) запись в базу
    track = Track(
        title=title,
        artist=artist,
        album=album,
        genre=genre,
        file="/" + audio_path.replace("\\", "/"),   # для URL
        cover="/" + cover_path.replace("\\", "/"),
        user_id=user_id,
    )
    db.add(track)
    db.commit()
    db.refresh(track)

    return track

# ──────────────────────────────────────────────
# Роут: получить список треков
# ──────────────────────────────────────────────
@app.get("/tracks", response_model=List[TrackOut])
def list_tracks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tracks = db.query(Track).offset(skip).limit(limit).all()
    return tracks
