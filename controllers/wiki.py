from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.wiki import WikiCreateRequest
from models.db import get_db
from utils.jwt import verify_token
from utils.logger import logger

router = APIRouter(prefix="/api/wiki", tags=["Wiki"])


@router.post("/create-wiki")
async def create_wiki(
    body: WikiCreateRequest, db: Session = Depends(get_db), token=Depends(verify_token)
):
    response = {}
    try:
        pass
    except Exception as e:
        logger.error(e)
    finally:
        return response
