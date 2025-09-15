from pydantic import BaseModel, EmailStr, constr
from uuid import UUID
from typing import Optional, List

from enums import UserRole


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


class UserForgotPasswordRequest(BaseModel):
    userEmail: EmailStr


class UserVerifyCodeRequest(BaseModel):
    userEmail: EmailStr
    userVerificationCode: str


class UserUpdatePasswordRequest(BaseModel):
    userEmail: EmailStr
    userPassword: str = constr(min_length=6, max_length=32)
    userConfirmPassword: str = constr(min_length=6, max_length=32)


class UserInviteRequest(BaseModel):
    userEmail: List[EmailStr]
    fromUserId: UUID
    userRole: UserRole
    tenantId: UUID


class UserActivateRequest(BaseModel):
    userEmail: EmailStr
    userToken: str
    userPassword: str = constr(min_length=6, max_length=32)
    userConfirmPassword: str = constr(min_length=6, max_length=32)
