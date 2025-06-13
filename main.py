import os, shutil, time
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import Session as DB, init_db
import models, schemas

SECRET_KEY = os.getenv("SECRET_KEY", "change_me_secret")
ALGORITHM  = "HS256"

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2  = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"],
    allow_headers=["*"], allow_credentials=True
)

def get_db():
    db = DB()
    try:
        yield db
    finally:
        db.close()

def create_token(data: dict):
    return jwt.encode({**data, "iat": time.time()}, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    email = verify_token(token)
    user  = db.query(models.User).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.get("/")
def root():
    return {"message": "Loop backend is running"}

# ---------- Auth ----------
@app.post("/register")
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter_by(email=data.email).first():
        raise HTTPException(400, "Email already exists")
    hashed = pwd_ctx.hash(data.password)
    db.add(models.User(email=data.email, password=hashed))
    db.commit()
    return {"msg": "registered"}

@app.post("/login", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=form.username).first()
    if not user or not pwd_ctx.verify(form.password, user.password):
        raise HTTPException(401, "Bad credentials")
    token = create_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

# ---------- Music ----------
UPLOADS = "uploads"
os.makedirs(UPLOADS, exist_ok=True)

@app.post("/upload")
def upload(title: str = Form(...), artist: str = Form(...),
           file: UploadFile = File(...),
           user: models.User = Depends(get_current_user),
           db: Session = Depends(get_db)):
    path = os.path.join(UPLOADS, file.filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    track = models.Track(title=title, artist=artist, filename=file.filename)
    db.add(track); db.commit(); db.refresh(track)
    return track

@app.get("/tracks", response_model=list[schemas.TrackOut])
def tracks(db: Session = Depends(get_db),
           user: models.User = Depends(get_current_user)):
    return db.query(models.Track).all()
