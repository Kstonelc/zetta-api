"""
@File        : utils/jwt.py
@Description : jwt工具类
@Author      : Kstone
@Date        : 2025/07/11
"""

import jwt
from fastapi import Request
from exceptions import AuthTokenException
from datetime import datetime, timedelta, UTC
from typing import Optional

SECRET_KEY = "zetta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 一周


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        # Token 过期
        return None
    except jwt.InvalidTokenError:
        # 无效 Token
        return None


# 用于验证Token
def verify_token(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise AuthTokenException(message="缺少或无效的 Authorization 头")

    token = auth[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print(payload)
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthTokenException(message="Token已过期")
    except jwt.InvalidTokenError:
        raise AuthTokenException(message="Token无效")
