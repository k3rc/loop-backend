from pydantic import BaseModel

class MusicCreate(BaseModel):
    title: str
    artist: str
    filename: str
