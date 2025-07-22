from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session, joinedload
from schemas.user import UserEmailRegisterRequest, UserEmailLoginRequest
from models.db import get_db
from models.user import User
from utils.common import hash_password, verify_password
from utils.jwt import create_access_token
from utils.logger import logger

router = APIRouter(prefix="/api/user", tags=["User"])


@router.post("/find-user")
async def find_user(body: Request, db: Session = Depends(get_db)):
    response = {}
    try:
        user = (
            db.query(User)
            .options(joinedload(User.tenants))
            .filter(User.active.is_(True), User.email == "2609753201@qq.com")
            .first()
        )
        response = {"ok": True, "data": user}
    except Exception as e:
        response = {"ok": False, "message": "获取用户信息失败"}
        logger.error(e)
    finally:
        return response


@router.post("/email-signup")
async def sign_up(body: UserEmailRegisterRequest, db: Session = Depends(get_db)):
    response = {}
    try:
        user_email = body.userEmail
        user_password = body.userPassword

        if (
            db.query(User)
            .filter(User.active.is_(True), User.email == user_email)
            .first()
        ):
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


@router.post("/email-login")
async def email_login(body: UserEmailLoginRequest, db: Session = Depends(get_db)):
    response = {}
    try:
        user_email = body.userEmail
        user_password = body.userPassword

        user = (
            db.query(User)
            .filter(User.active.is_(True), User.email == user_email)
            .first()
        )
        if not user:
            response = {"ok": False, "message": "用户不存在"}
            return

        if not verify_password(user_password, user.password):
            response = {"ok": False, "message": "密码错误"}
            return

        # 生成jwt
        access_token = create_access_token(data={"email": user_email})

        response = {
            "ok": True,
            "data": {
                "access_token": access_token,
            },
        }

    except Exception as e:
        db.rollback()
        logger.error(e)
        response = {"ok": False, "message": "登录失败"}

    finally:
        return response
