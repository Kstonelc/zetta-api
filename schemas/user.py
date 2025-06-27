from pydantic import BaseModel


class UserRequest(BaseModel):
    username: str
    email: str
