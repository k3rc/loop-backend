from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DB_URL = "sqlite:///./music.db"
engine  = create_engine(DB_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base    = declarative_base()

def init_db():
    from models import User, Track   # noqa
    Base.metadata.create_all(bind=engine)
