from fastapi import FastAPI, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil, os

# если не подключено:
from sqlalchemy.orm import Session
from models import Track                # твоя ORM‑модель
from database import get_db             # твой dependency
from auth import verify_token           # функция проверки токена
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://loop-frontend-three.vercel.app"],
    # для локалки удобно добавить "http://localhost:3000"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# папка uploads будет доступна по URL /uploads/...
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
@app.post("/upload")
async def upload_track(
    title:  str = Form(...),
    artist: str = Form(...),
    album:  str = Form(...),
    genre:  str = Form(...),
    file:   UploadFile = File(...),
    cover:  UploadFile = File(...),
    token:  str = Form(...),
    db: Session = Depends(get_db)
):
    # 1) авторизуем пользователя
    user_id = verify_token(token)

    # 2) сохраняем файлы
    os.makedirs("uploads", exist_ok=True)
    audio_path = f"uploads/{file.filename}"
    cover_path = f"uploads/{cover.filename}"

    with open(audio_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    with open(cover_path, "wb") as f:
        shutil.copyfileobj(cover.file, f)

    # 3) заносим в БД
    track = Track(
        title=title,
        artist=artist,
        album=album,
        genre=genre,
        file="/" + audio_path,     # "/uploads/xxx.mp3"
        cover="/" + cover_path,    # "/uploads/xxx.jpg"
        user_id=user_id,
    )
    db.add(track)
    db.commit()
    db.refresh(track)
    return track
from schemas import TrackOut  # Pydantic‑схема для ответа (создай, если нет)

@app.get("/tracks", response_model=list[TrackOut])
def list_tracks(skip: int = 0, limit: int = 100,
                db: Session = Depends(get_db)):
    return db.query(Track).offset(skip).limit(limit).all()
