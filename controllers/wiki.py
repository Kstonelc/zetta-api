from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.user import UserQueryRequest
from models.db import get_db
from utils.jwt import verify_token
from utils.logger import logger

router = APIRouter(prefix="/api/wiki", tags=["Wiki"])


@router.post("/create-wiki")
async def find_user(
    body: UserQueryRequest, db: Session = Depends(get_db), token=Depends(verify_token)
):
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
