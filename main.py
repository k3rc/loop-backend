from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from models import Track
from database import SessionLocal, engine
from schemas import TrackCreate
from config import SECRET_KEY
from jose import jwt
import shutil, os

Track.metadata.create_all(bind=engine)
app = FastAPI()

origins = [
    "https://loop-frontend-three.vercel.app",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/upload")
async def upload_track(
    title: str = Form(...),
    artist: str = Form(...),
    album: str = Form(...),
    genre: str = Form(...),
    file: UploadFile = File(...),
    cover: UploadFile = File(...),
    token: str = Form(...),
    db=Depends(get_db)
):
    user_id = verify_token(token)
    audio_path = f"uploads/audio_{file.filename}"
    cover_path = f"uploads/cover_{cover.filename}"
    with open(audio_path, "wb") as f: shutil.copyfileobj(file.file, f)
    with open(cover_path, "wb") as f: shutil.copyfileobj(cover.file, f)
    track = Track(title=title, artist=artist, album=album, genre=genre,
                  file="/" + audio_path, cover="/" + cover_path, user_id=user_id)
    db.add(track)
    db.commit()
    db.refresh(track)
    return track

@app.get("/tracks")
def get_tracks(token: str, db=Depends(get_db)):
    user_id = verify_token(token)
    return db.query(Track).filter(Track.user_id == user_id).all()

@app.get("/")
def root():
    return {"status": "ok"}
