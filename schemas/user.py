from pydantic import BaseModel, EmailStr, constr
from typing import Optional


class UserEmailRegisterRequest(BaseModel):
    userName: str
    userEmail: EmailStr
    userPassword: str = constr(min_length=6, max_length=32)
    userConfirmPassword: str = constr(min_length=6, max_length=32)


class UserEmailLoginRequest(BaseModel):
    userEmail: EmailStr
    userPassword: str = constr(min_length=6, max_length=32)  # 规则验证


class UserQueryRequest(BaseModel):
    userId: Optional[int] = None
    userEmail: Optional[EmailStr] = None

    def has_valid_key(self) -> bool:
        return self.userId is not None or self.userEmail is not None
