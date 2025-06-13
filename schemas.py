from pydantic import BaseModel

class TrackCreate(BaseModel):
    title: str
    artist: str
    album: str
    genre: str
