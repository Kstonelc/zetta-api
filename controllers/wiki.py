from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.user import UserRegisterRequest, UserQueryRequest
from models.db import get_db
from models.user import User
from utils.common import hash_password
from utils.logger import logger

router = APIRouter(prefix="/wiki", tags=["Wiki"])


@router.post("/create-wiki")
async def find_user(user: UserQueryRequest, db: Session = Depends(get_db)):
    pass
