from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"
    id       = Column(Integer, primary_key=True, index=True)
    email    = Column(String, unique=True, index=True)
    password = Column(String)

class Track(Base):
    __tablename__ = "tracks"
    id       = Column(Integer, primary_key=True, index=True)
    title    = Column(String)
    artist   = Column(String)
    genre    = Column(String)
    album    = Column(String)
    filename = Column(String)
    cover    = Column(String)
