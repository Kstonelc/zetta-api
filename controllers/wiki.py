from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.wiki import WikiCreateRequest
from models import Wiki, get_db
from utils.jwt import verify_token
from utils.logger import logger

router = APIRouter(prefix="/api/wiki", tags=["Wiki"])


@router.post("/create-wiki")
async def create_wiki(
    body: WikiCreateRequest, db: Session = Depends(get_db), token=Depends(verify_token)
):
    response = {}
    try:
        wikiName = body.wikiName
        wikiDesc = body.wikiDesc if body.wikiDesc else ""
        wikiType = body.wikiType
        wikiEmbeddingId = body.wikiEmbeddingId
        wikiRerankId = body.wikiRerankId
        wikiSimThresh = body.wikiSimThresh

        if db.query(Wiki).filter(Wiki.active.is_(True), Wiki.name == wikiName).first():
            response = {"ok": False, "message": "知识库已存在"}
            return

        new_wiki = Wiki(
            active=True,
            name=wikiName,
            desc=wikiDesc,
            type=wikiType,
            embedding_id=wikiEmbeddingId,
            rerank_id=wikiRerankId,
            sim_thresh=wikiSimThresh,
        )
        db.add(new_wiki)
        db.commit()
        db.refresh(new_wiki)

        response = {"ok": True, "data": new_wiki.id, "message": "创建成功"}
    except Exception as e:
        logger.error(e)
    finally:
        return response
