from sqlalchemy import Column, Integer, String
from database import Base

class Track(Base):
    __tablename__ = "tracks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    artist = Column(String)
    album = Column(String)
    genre = Column(String)
    file_path = Column(String)
    cover_path = Column(String)
    user_id = Column(Integer)

    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "genre": self.genre,
            "file": f"/file/{self.file_path.split('/')[-1]}",
            "cover": f"/file/{self.cover_path.split('/')[-1]}"
        }
