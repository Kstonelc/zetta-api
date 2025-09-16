from fastapi import APIRouter, Depends, Request, BackgroundTasks
from lxml.html.diff import token
from sqlalchemy.orm import Session, joinedload

from enums import UserStatus
from models.join import TenantUserJoin
from schemas.user import (
    UserEmailRegisterRequest,
    UserEmailLoginRequest,
    UserQueryRequest,
    UserForgotPasswordRequest,
    UserVerifyCodeRequest,
    UserUpdatePasswordRequest,
    UserInviteRequest,
    UserActivateRequest,
)
from fastapi.encoders import jsonable_encoder
from models.db import get_db
from models.user import User
from config import settings
from utils.common import hash_password, verify_password, generate_random_code
from utils.jwt import create_access_token, verify_token, decode_token
from utils.logger import logger
from utils.email import send_verify_code, send_invite_url

router = APIRouter(prefix="/api/user", tags=["User"])


@router.post("/find-user")
async def find_user(
    body: UserQueryRequest, db: Session = Depends(get_db), token=Depends(verify_token)
):
    response = {}
    try:
        user_email = body.userEmail if body.userEmail else None

        user = (
            db.query(User)
            .options(joinedload(User.tenants))
            .filter(
                User.active.is_(True),
                User.email == user_email,
                User.status == UserStatus.Active.value,
            )
            .first()
        )
        if not user:
            response = {"ok": False, "message": "用户不存在"}
            return

        user_data = jsonable_encoder(user)
        current_tenant = jsonable_encoder(user.current_tenant)
        user_data["role"] = user.get_role(current_tenant.get("id"))
        user_data["current_tenant"] = current_tenant
        response = {"ok": True, "data": user_data}
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
            .filter(
                User.active.is_(True),
                User.email == user_email,
                User.status == UserStatus.Active.value,
            )
            .first()
        )
        if not user:
            response = {"ok": False, "message": "用户不存在"}
            return

        if not verify_password(user_password, user.password):
            response = {"ok": False, "message": "密码错误"}
            return

        # TODO 目前只设计一个租户的情况
        current_tenant_id = user.current_tenant.id

        # 生成jwt
        access_token = create_access_token(
            data={"email": user_email, "tenant_id": str(current_tenant_id)}
        )
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


@router.post("/send-verification-code")
async def send_verification_code(
    background_tasks: BackgroundTasks,
    body: UserForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    response = {}
    try:
        # 验证码10分钟过期 后期使用redis实现
        user_email = body.userEmail

        verification_code = generate_random_code()
        user = (
            db.query(User)
            .filter(User.active.is_(True), User.email == user_email)
            .first()
        )
        if not user:
            response = {"ok": False, "message": "用户不存在"}
            return
        if user.status != UserStatus.Active.value:
            response = {"ok": False, "message": "用户未激活"}
            return
        user.secret = verification_code
        db.commit()
        send_verify_code(background_tasks, user_email, verification_code)
        response = {"ok": True, "message": "验证码已发送"}
    except Exception as e:
        db.rollback()
        logger.error(e)
        response = {"ok": False, "message": "验证码发送失败"}

    finally:
        return response


@router.post("/verify-code")
async def verify_code(body: UserVerifyCodeRequest, db: Session = Depends(get_db)):
    response = {}
    try:
        user_email = body.userEmail
        user_verification_code = body.userVerificationCode

        user = (
            db.query(User)
            .filter(User.active.is_(True), User.email == user_email)
            .first()
        )
        if not user:
            response = {"ok": False, "message": "用户不存在"}
            return
        if user.status != UserStatus.Active.value:
            response = {"ok": False, "message": "用户未激活"}
            return
        if user.secret != user_verification_code:
            response = {"ok": False, "message": "验证码错误"}
            return

        response = {"ok": True, "data": "验证成功"}

    except Exception as e:
        logger.error(e)
        response = {"ok": False, "message": "登录失败"}

    finally:
        return response


@router.post("/update-user-password")
async def update_user_password(
    body: UserUpdatePasswordRequest, db: Session = Depends(get_db)
):
    response = {}
    try:
        user_email = body.userEmail
        user_password = body.userPassword
        user_confirm_password = body.userConfirmPassword

        if user_password != user_confirm_password:
            response = {"ok": False, "message": "密码不一致"}
            return

        user = (
            db.query(User)
            .filter(
                User.active.is_(True),
                User.email == user_email,
                User.status == UserStatus.Active.value,
            )
            .first()
        )
        if not user:
            response = {"ok": False, "message": "用户不存在"}
            return
        user.password = hash_password(user_password)
        db.commit()
        response = {"ok": True, "data": "密码重置成功"}
    except Exception as e:
        db.rollback()
        logger.error(e)
        response = {"ok": False, "message": "重置密码失败"}
    finally:
        return response


@router.post("/invite-user")
async def invite_user(
    background_tasks: BackgroundTasks,
    body: UserInviteRequest,
    db: Session = Depends(get_db),
):
    response = {}
    try:
        user_email_list = body.userEmail
        from_user_id = body.fromUserId
        user_role = body.userRole
        tenant_id = body.tenantId

        from_user = db.get(User, from_user_id)
        if from_user.email in user_email_list:
            response = {"ok": False, "message": "不能邀请自己"}
            return
        for email in user_email_list:
            user = db.query(User).filter(User.email == email).first()
            if user:
                # 重新发送邀请邮件
                token = create_access_token(
                    data={"email": email, "tenant_id": str(tenant_id)}
                )
                send_invite_url(
                    background_tasks,
                    email,
                    f"{settings.BASE_URL}/user/activate?email={email}&token={token}",
                )
                user_email_list.remove(email)

        users = [
            User(
                name=email,
                email=email,
                password=hash_password(email),
                status=UserStatus.Pending,
                active=True,
                tenant_user_joins=[
                    TenantUserJoin(
                        tenant_id=tenant_id,
                        role=user_role,
                        invited_by=from_user_id,
                        current=True,
                        active=True,
                    )
                ],
            )
            for email in user_email_list
        ]

        db.add_all(users)
        db.flush()
        db.commit()
        # 发送邀请邮件
        for email in user_email_list:
            token = create_access_token(
                data={"email": email, "tenant_id": str(tenant_id)}
            )
            send_invite_url(
                background_tasks,
                email,
                f"{settings.BASE_URL}/user/activate?email={email}&token={token}",
            )
        response = {"ok": True, "data": "邀请成功", "message": "邀请成功"}
    except Exception as e:
        db.rollback()
        logger.error(e)
        response = {"ok": False, "message": "邀请用户失败"}
    finally:
        return response


@router.post("/activate")
async def activate(body: UserActivateRequest, db: Session = Depends(get_db)):
    response = {}
    try:
        user_email = body.userEmail
        user_token = body.userToken
        user_password = body.userPassword
        user_confirm_password = body.userConfirmPassword

        if user_password != user_confirm_password:
            response = {"ok": False, "message": "密码不一致"}
            return
        # 解析 user_token
        token_payload = decode_token(user_token)
        tenant_id = token_payload.get("tenant_id")
        if not tenant_id:
            response = {"ok": False, "message": "无效的激活链接"}
            return
        user = (
            db.query(User)
            .filter(
                User.active.is_(True),
                User.email == user_email,
                User.status == UserStatus.Pending,
            )
            .first()
        )
        if not user:
            response = {"ok": False, "message": "激活用户不存在"}
            return
        user.status = UserStatus.Active.value
        user.password = hash_password(user_password)
        db.commit()
        response = {"ok": True, "data": "激活成功", "message": "激活成功"}
    except Exception as e:
        db.rollback()
        logger.error(e)
        response = {"ok": False, "message": "激活用户失败"}
    finally:
        return response
