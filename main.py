from fastapi import (
    FastAPI, UploadFile, File, Form,
    Depends, HTTPException, status
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import os
import shutil
from sqlalchemy.orm import Session

# ──────────────────────────────────────────────
# DB, модели и схемы
# ──────────────────────────────────────────────
from database import Base, engine, get_db          # Base & get_db из database.py
from models import Track                           # ORM‑модель
from schemas import TrackOut                       # Pydantic‑схема
from auth import verify_token                      # проверка Telegram‑токена

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

#
