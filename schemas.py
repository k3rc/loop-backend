from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type:   str

class TrackOut(BaseModel):
    id: int
    title: str
    artist: str
    filename: str
    class Config:
        orm_mode = True
