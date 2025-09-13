# schemas.py
from pydantic import BaseModel

class Place(BaseModel):
    id: int
    name: str
    category: str
    lat: float
    lon: float
    photo_url: Optional[str]
    review: str
    username: str

    class Config:
        orm_mode = True