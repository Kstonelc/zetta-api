from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED


class AuthTokenException(HTTPException):
    def __init__(
        self, status_code: int = HTTP_401_UNAUTHORIZED, message: str = "Token认证失败"
    ):
        super().__init__(status_code=status_code, detail=message)
