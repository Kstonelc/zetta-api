from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
from schemas.wiki import WikiCreateRequest, WikiQueryRequest
from models import Wiki, get_db
from enums import FileType
from uuid import uuid4
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


# 嵌入文档
@router.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token=Depends(verify_token),
):
    response = {}
    try:
        # TODO 这样处理不安全
        file_name = file.filename.split(".")[0]
        ext = Path(file.filename).suffix

        allowed_ext = FileType.get_suffixs()
        if ext not in allowed_ext:
            response = {
                "ok": False,
                "message": f"不支持的文件类型: {ext}, 仅支持: {', '.join(allowed_ext)}",
            }
            return
        saved_path = Path("./data") / f"{file_name}{ext}"

        # 保存文件到本地
        with saved_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(111, {
                "fileName": file_name,
                "filePath": str(saved_path),
                "fileExt": ext,
                "fileSize": saved_path.stat().st_size,
            })
        response = {
            "ok": True,
            "data": {
                "fileName": file_name,
                "filePath": str(saved_path),
                "fileExt": ext,
                "fileSize": round(saved_path.stat().st_size / 1024, 1),
            },
            "message": "文件上传成功"
        }
    except Exception as e:
        print(e)
        logger.error(e)
        response = {"ok": False, "message": "嵌入失败, 请稍候重试"}
    finally:
        return response
