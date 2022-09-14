
from pydantic import BaseModel
from typing import Optional

# Create User Model
class User(BaseModel):
    name: str
    email: str
    phoneNumber: str
    photoUrl: str

class Advert(BaseModel):
    title: str
    user: str
    description: Optional[str]
    location: Optional[str]
    coords: Optional[object] = {
        "lng": "0.0",
        "lat": "0.0"
    }
    photo: Optional[str]
    status: str
    timestamp: int