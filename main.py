from fastapi import FastAPI, UploadFile, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import FileResponse
from jose import jwt
import os, shutil

from database import init_db, SessionLocal
from models import Track
from schemas import TrackCreate
from config import SECRET_KEY, ALGORITHM, UPLOAD_DIR

app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload.get("sub"))
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/upload")
async def upload_track(
    title: str = Form(...),
    artist: str = Form(...),
    album: str = Form(...),
    genre: str = Form(...),
    file: UploadFile = Form(...),
    cover: UploadFile = Form(...),
    user_id: int = Depends(get_current_user_id)
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    track_path = os.path.join(UPLOAD_DIR, file.filename)
    cover_path = os.path.join(UPLOAD_DIR, cover.filename)

    with open(track_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    with open(cover_path, "wb") as f:
        shutil.copyfileobj(cover.file, f)

    db = SessionLocal()
    track = Track(
        title=title, artist=artist, album=album, genre=genre,
        file_path=track_path, cover_path=cover_path, user_id=user_id
    )
    db.add(track)
    db.commit()
    db.refresh(track)
    db.close()
    return {"message": "Uploaded", "track": track.id}

@app.get("/tracks")
def get_tracks(user_id: int = Depends(get_current_user_id)):
    db = SessionLocal()
    tracks = db.query(Track).filter(Track.user_id == user_id).all()
    db.close()
    return [t.as_dict() for t in tracks]

@app.get("/file/{filename}")
def serve_file(filename: str):
    return FileResponse(os.path.join(UPLOAD_DIR, filename))
