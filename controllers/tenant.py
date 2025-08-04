from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, selectinload, with_loader_criteria
from fastapi import Request
from enums import UserRole
from models import TenantUserJoin, Tenant, User, get_db
from schemas.tenant import TenantQueryRequest, TenantUpdateRequest
from utils.jwt import verify_token
from utils.logger import logger

router = APIRouter(prefix="/api/tenant", tags=["Tenant"])


@router.post("/find-admin")
async def find_admin(body: Request, db: Session = Depends(get_db)):
    # Tips: 使用 Request 跳过入参验证
    response = {}
    try:
        res = (
            db.query(TenantUserJoin)
            .filter(TenantUserJoin.role == UserRole.Admin.value)
            .first()
        )
        if not res:
            response = {"ok": False, "message": "管理员不存在"}
        else:
            response = {"ok": True, "data": "管理员存在"}
    except Exception as e:
        logger.error(e)
    finally:
        return response


@router.post("/find-tenant")
async def find_users(
    body: TenantQueryRequest, db: Session = Depends(get_db), token=Depends(verify_token)
):
    response = {}
    try:
        tenantId = body.tenantId

        tenant = (
            db.query(Tenant)
            .options(
                selectinload(Tenant.users),
                with_loader_criteria(User, User.active.is_(True)),
            )
            .filter(Tenant.id == tenantId)
            .first()
        )
        users = []
        for user in tenant.users:
            role = user.get_role(tenantId)
            user.role = role
            users.append(user)
        tenant.users = users

        response = {"ok": True, "data": tenant}
    except Exception as e:
        response = {"ok": False, "message": "获取用户信息失败"}
        logger.error(e)
    finally:
        return response


@router.post("/update-tenant")
async def update_tenant(
    body: TenantUpdateRequest,
    db: Session = Depends(get_db),
    token=Depends(verify_token),
):
    response = {}
    try:
        tenantId = body.tenantId
        tenantName = body.tenantName

        tenant = db.query(Tenant).filter(Tenant.id == tenantId).first()

        if not tenant:
            response = {"ok": False, "message": "租户不存在"}
            return

        tenant.name = tenantName
        db.commit()
        db.refresh(tenant)

        tenant = (
            db.query(Tenant)
            .options(
                selectinload(Tenant.users),
                with_loader_criteria(User, User.active.is_(True)),
            )
            .filter(Tenant.id == tenantId)
            .first()
        )

        response = {"ok": True, "data": tenant}
    except Exception as e:
        db.rollback()
        response = {"ok": False, "message": "获取用户信息失败"}
        logger.error(e)
    finally:
        return response
