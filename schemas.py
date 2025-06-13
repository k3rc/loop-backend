from pydantic import BaseModel

class TrackCreate(BaseModel):
    title: str
    artist: str
    album: str
    genre: str
    cover_url: str
    user_id: str

class TrackResponse(TrackCreate):
    id: int
    filename: str

    class Config:
        orm_mode = True
