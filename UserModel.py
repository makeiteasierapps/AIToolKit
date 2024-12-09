from pydantic import BaseModel
from bson import ObjectId

class User(BaseModel):
    user_id: str
    username: str
    api_request_count: int
    disabled: bool = False
    hashed_password: str
