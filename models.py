# models.py
from pydantic import BaseModel
from typing import Optional

class UserAuth(BaseModel):
    telegram_id: int
    username: Optional[str] = None

class PlaceCreate(BaseModel):
    name: str
    category: str
    lat: float
    lon: float
    photo_url: Optional[str] = None
    review: str
    user_id: int