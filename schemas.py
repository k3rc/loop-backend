from pydantic import BaseModel

class TrackCreate(BaseModel):
    title: str
    artist: str
    genre: str
    album: str
    filename: str
    cover: str

class TrackOut(TrackCreate):
    id: int
    class Config:
        orm_mode = True
