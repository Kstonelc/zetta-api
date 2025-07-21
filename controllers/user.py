from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.user import UserRegisterRequest, UserQueryRequest
from models.db import get_db
from models.user import User
from utils.common import hash_password
from utils.logger import logger

router = APIRouter(prefix="/api/user", tags=["User"])


@router.post("/find-user")
async def find_user(body: UserQueryRequest, db: Session = Depends(get_db)):
    response = {}
    try:
        if not body.has_valid_key():
            response = {"ok": False, "message": "必须提供 id 或 email"}
            return
    except Exception as e:
        logger.error(e)
    finally:
        return response


@router.post("/sign-up")
async def sign_up(body: UserRegisterRequest, db: Session = Depends(get_db)):
    response = {}
    try:
        user_email = body.userEmail
        user_password = body.userPassword

        if db.query(User).filter(User.email == user_email).first():
            response = {"ok": False, "message": "用户已存在"}
            return

        new_user = User(
            email=body.userEmail, password=hash_password(user_password), active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        response = {"ok": True, "data": new_user.id, "message": "注册成功"}

    except Exception as e:
        db.rollback()
        logger.error(e)
        response = {"ok": False, "message": "注册失败"}

    finally:
        return response
