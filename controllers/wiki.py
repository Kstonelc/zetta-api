from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.user import UserQueryRequest
from models.db import get_db
from utils.jwt import verify_token
from utils.logger import logger

router = APIRouter(prefix="/api/wiki", tags=["Wiki"])


@router.post("/create-wiki")
async def find_user(
    user: UserQueryRequest, db: Session = Depends(get_db), token=Depends(verify_token)
):
    pass
