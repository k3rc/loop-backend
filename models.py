from sqlalchemy import Column, Integer, String
from database import Base

class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    artist = Column(String)
    album = Column(String)
    genre = Column(String)
    filename = Column(String)
    cover_url = Column(String)
    user_id = Column(String)
