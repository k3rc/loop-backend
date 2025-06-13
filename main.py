import os, shutil, time
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import models, schemas
from database import Session as DB, init_db

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM  = "HS256"
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2  = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_token(data: dict):
    return jwt.encode({**data, "iat": time.time()}, SECRET_KEY, algorithm=ALGORITHM)

def verify(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])["sub"]
    except JWTError:
        raise HTTPException(401, "Invalid token")

def get_db():
    db = DB()
    try: yield db
    finally: db.close()

# ---- корневой маршрут
@app.get("/")
def root(): return {"message": "Loop backend running"}

# ---- загрузка из Telegram‑бота (без авторизации)
@app.post("/bot/upload")
def bot_upload(data: schemas.TrackCreate, db: Session = Depends(get_db)):
    track = models.Track(**data.dict())
    db.add(track); db.commit(); db.refresh(track)
    return track

# ---- WebApp авторизация (упрощённо: 1 пользователь demo/demo)
@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    if form.username == "demo" and form.password == "demo":
        return {"access_token": create_token({"sub": "demo"}), "token_type": "bearer"}
    raise HTTPException(401, "Bad credentials")

def current_user(token: str = Depends(oauth2)): verify(token); return "demo"

# ---- WebApp загрузка через форму
@app.post("/upload", response_model=schemas.TrackOut)
def upload(title: str = Form(...), artist: str = Form(...),
           genre: str = Form(...), album: str = Form(...),
           file: UploadFile = File(...), cover: UploadFile = File(...),
           db: Session = Depends(get_db), user: str = Depends(current_user)):
    fname = f"{int(time.time())}_{file.filename}"
    cvr   = f"{int(time.time())}_{cover.filename}"
    shutil.copyfileobj(file.file, open(os.path.join(UPLOAD_DIR, fname), "wb"))
    shutil.copyfileobj(cover.file, open(os.path.join(UPLOAD_DIR, cvr), "wb"))
    tr = models.Track(title=title, artist=artist, genre=genre,
                      album=album, filename=fname, cover=cvr)
    db.add(tr); db.commit(); db.refresh(tr)
    return tr

# ---- список треков
@app.get("/tracks", response_model=list[schemas.TrackOut])
def tracks(db: Session = Depends(get_db), user: str = Depends(current_user)):
    return db.query(models.Track).all()
