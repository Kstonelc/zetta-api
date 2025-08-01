from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import Request
from enums import TenantUserRole
from models import TenantUserJoin, Tenant, get_db
from schemas.tenant import TenantQueryRequest
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
            .filter(TenantUserJoin.role == TenantUserRole.Admin.value)
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


@router.post("/find-users")
async def find_users(
    body: TenantQueryRequest, db: Session = Depends(get_db), token=Depends(verify_token)
):
    response = {}
    try:
        tenantId = body.tenantId

        tenant = db.query(Tenant).filter(Tenant.id == tenantId).first()

        response = {"ok": True, "data": tenant.users}
    except Exception as e:
        response = {"ok": False, "message": "获取用户信息失败"}
        logger.error(e)
    finally:
        return response
