from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from pathlib import Path
import shutil

from schemas.wiki import (
    WikiCreateRequest,
    WikiQueryRequest,
    WikiPreviewFileChunkRequest,
    WikiIndexFileRequest,
    WikiRecallDocsRequest,
)
from celery_task.tasks import long_running_task
from models import Wiki, get_db
from enums import FileType, WikiChunkType
from utils.jwt import verify_token
from langchain_community.vectorstores import Qdrant
from qdrant_client.http.models import Distance
from config import settings
from llm.qwen import QWEmbeddings
from utils.logger import logger
from utils.rag import load_doc, split_doc, split_doc_with_parents

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
        response = {
            "ok": True,
            "data": {
                "fileName": file_name,
                "filePath": saved_path.as_posix(),
                "fileExt": ext,
                # 默认单位为 KB
                "fileSize": round(saved_path.stat().st_size / 1024, 1),
            },
            "message": "文件上传成功",
        }
    except Exception as e:
        logger.error(e)
        response = {"ok": False, "message": "上传失败, 请稍候重试"}
    finally:
        return response


@router.post("/preview-file-chunks")
async def preview_file_chunks(
    body: WikiPreviewFileChunkRequest,
    db: Session = Depends(get_db),
    token=Depends(verify_token),
):
    response = {}
    try:
        file_path = body.filePath
        chunk_type = body.chunkType
        chunk_size = body.chunkSize
        chunk_overlap = body.chunkOverlap
        parent_chunk_size = body.parentChunkSize
        parent_chunk_overlap = body.parentChunkOverlap
        child_chunk_size = body.childChunkSize
        child_chunk_overlap = body.childChunkOverlap

        doc = load_doc(file_path)
        match chunk_type:
            case WikiChunkType.Classical.value:
                split_docs = split_doc(doc, chunk_size, chunk_overlap)
            case WikiChunkType.ParentChild.value:
                split_docs = split_doc_with_parents(
                    doc,
                    parent_chunk_size,
                    parent_chunk_overlap,
                    child_chunk_size,
                    child_chunk_overlap,
                )

        response = {
            "ok": True,
            "data": split_docs,
        }
    except Exception as e:
        logger.error(e)
        response = {"ok": False, "message": "预览块失败"}
    finally:
        return response


@router.post("/index-file")
async def index_file(
    body: WikiIndexFileRequest,
    db: Session = Depends(get_db),
    token=Depends(verify_token),
):
    response = {}
    try:
        docs = body.docs
        api_key = body.apiKey

        # 1 切割文档

        # 2 向量化处理
        qw_embedding = QWEmbeddings(
            api_key=settings.QIANWEN_API_KEY, model="text-embedding-v1"
        )
        vector_db_url = f"http://{settings.VECTOR_DB_HOST}:{settings.VECTOR_DB_PORT}"
        vs = Qdrant.from_documents(
            documents=docs,
            embedding=qw_embedding,
            url=vector_db_url,
            collection_name="bichon",
            distance_func=Distance.COSINE,
        )
        vs.add_documents(docs)
        response = {
            "ok": True,
            "data": [],
        }
    except Exception as e:
        logger.error(e)
        response = {"ok": False, "message": "索引文件失败"}
    finally:
        return response


@router.post("/recall-docs")
def recall_docs(
    body: WikiRecallDocsRequest,
    db: Session = Depends(get_db),
    token=Depends(verify_token),
):
    response = {}
    try:
        wiki_name = body.wikiName
        query_content = body.queryContent

        qw_embedding = QWEmbeddings(
            api_key=settings.QIANWEN_API_KEY, model="text-embedding-v1"
        )
        vector_db_url = f"http://{settings.VECTOR_DB_HOST}:{settings.VECTOR_DB_PORT}"
        vs = Qdrant.from_existing_collection(
            embedding=qw_embedding,
            url=vector_db_url,
            path=None,
            collection_name=wiki_name,
        )

        docs_scores = vs.similarity_search_with_score(query_content, k=5)
        res = long_running_task.delay({"data": "test"})
        task_id = res.id
        print("任务Id", task_id)
        response = {
            "ok": True,
            "data": docs_scores,
        }
    except Exception as e:
        logger.error(e)
        response = {"ok": False, "message": "查询失败"}
    finally:
        return response
