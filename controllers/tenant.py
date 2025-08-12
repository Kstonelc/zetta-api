from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, selectinload, with_loader_criteria
from fastapi import Request
from enums import UserRole
from models import Tenant, User, TenantUserJoin, get_db
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
            .filter(TenantUserJoin.role == UserRole.Owner.value)
            .first()
        )
        if not res:
            response = {"ok": False, "message": "管理员不存在"}
        else:
            response = {"ok": True, "data": "管理员存在"}
        pass
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
                selectinload(Tenant.tenant_user_joins).joinedload(TenantUserJoin.user),
                with_loader_criteria(
                    User, lambda u: u.active.is_(True), include_aliases=True
                ),
            )
            .filter(Tenant.id == tenantId)
            .first()
        )
        users_with_roles = []
        for join in tenant.tenant_user_joins:
            if not join.user:
                continue
            if join.user.active:
                user_data = join.user.to_dict()
                user_data["role"] = join.role
                users_with_roles.append(user_data)

        response = {
            "ok": True,
            "data": {
                **tenant.to_dict(),
                "users": users_with_roles,
            },
        }
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
        response = {"ok": False, "message": "更新用户信息失败"}
        logger.error(e)
    finally:
        return response
