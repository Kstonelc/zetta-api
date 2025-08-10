from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.wiki import WikiCreateRequest, WikiQueryRequest
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
        tenant_id = body.tenantId
        user_id = body.userId
        wiki_name = body.wikiName
        wiki_desc = body.wikiDesc if body.wikiDesc else ""
        wiki_type = body.wikiType
        wiki_embedding_id = body.wikiEmbeddingId
        wiki_rerank_id = body.wikiRerankId
        wiki_sim_thresh = body.wikiSimThresh

        if db.query(Wiki).filter(Wiki.active.is_(True), Wiki.name == wiki_name).first():
            response = {"ok": False, "message": "知识库已存在"}
            return

        new_wiki = Wiki(
            active=True,
            name=wiki_name,
            desc=wiki_desc,
            user_id=user_id,
            tenant_id=tenant_id,
            type=wiki_type,
            embedding_id=wiki_embedding_id,
            rerank_id=wiki_rerank_id,
            sim_thresh=wiki_sim_thresh,
        )
        db.add(new_wiki)
        db.commit()

        response = {"ok": True, "data": new_wiki.id, "message": "创建成功"}
    except Exception as e:
        db.rollback()
        logger.error(e)
        response = {"ok": False, "message": "创建失败"}
    finally:
        return response


@router.post("/find-wikis")
async def find_wikis(
    body: WikiQueryRequest, db: Session = Depends(get_db), token=Depends(verify_token)
):
    response = {}
    try:
        tenant_id = body.tenantId

        wikis = (
            db.query(Wiki)
            .filter(
                Wiki.active.is_(True),
                Wiki.tenant_id == tenant_id,
            )
            .all()
        )
        response = {
            "ok": True,
            "data": wikis,
        }
    except Exception as e:
        logger.error(e)
        response = {"ok": False, "message": "查询失败"}
    finally:
        return response
