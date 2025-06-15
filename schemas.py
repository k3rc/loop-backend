from pydantic import BaseModel

class TrackOut(BaseModel):
    id: int
    title: str
    artist: str
    album: str
    genre: str
    file: str
    cover: str
    user_id: int

    class Config:
        orm_mode = True
