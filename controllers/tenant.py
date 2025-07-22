from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import Request
from models.db import get_db
from enums import TenantUserRole
from models.tenant import TenantUserJoin
from models.user import User
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
