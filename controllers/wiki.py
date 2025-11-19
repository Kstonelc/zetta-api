from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import insert
from pathlib import Path
import shutil
import uuid

from schemas.wiki import (
    WikiCreateRequest,
    WikiQueryRequest,
    WikiPreviewFileChunkRequest,
    WikiIndexDocumentRequest,
    WikiRecallDocsRequest,
)
from celery_task.tasks import long_running_task
from models import Wiki, get_db
from models.document import Document, ParentChunk, ChildChunk, DocumentIndexTask
from enums import FileType, WikiChunkType
from utils.jwt import verify_token
from langchain_community.vectorstores import Qdrant
from qdrant_client.http.models import Distance
from config import settings
from llm.qwen import QWEmbeddings
from utils.common import file_hash
from utils.logger import logger
from utils.rag import (
    load_doc,
    split_doc,
    preview_doc_with_parents,
    split_docs_with_parents,
)


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
        parent_chunk_size = body.parentChunkSize
        parent_chunk_overlap = body.parentChunkOverlap
        child_chunk_size = body.childChunkSize
        child_chunk_overlap = body.childChunkOverlap

        docs = load_doc(file_path)
        match chunk_type:
            case WikiChunkType.Classical.value:
                split_docs = split_doc(docs, parent_chunk_size, parent_chunk_overlap)
            case WikiChunkType.ParentChild.value:
                split_docs = preview_doc_with_parents(
                    docs,
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


@router.post("/index-document")
async def index_document(
    body: WikiIndexDocumentRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    token=Depends(verify_token),
):
    response = {}
    try:
        background_tasks.add_task(run_document_index_task, body, db)
        response = {
            "ok": True,
            "data": "文件索引成功",
        }
    except Exception as e:
        logger.error(e)
        response = {"ok": False, "message": "索引文件失败"}
    finally:
        return response


@router.post("/index-document/progress")
async def index_document_progress(
    body: WikiIndexDocumentRequest, db: Session = Depends(get_db)
):
    response = {}
    try:
        wiki_id = body.wikiId

        document_index_tasks = (
            db.query(DocumentIndexTask)
            .filter(DocumentIndexTask.wiki_id == wiki_id)
            .all()
        )
    except Exception as e:
        logger.error(e)
        response = {"ok": False, "message": "索引查询失败"}
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
            collection_name="bichon",
        )

        docs_scores = vs.similarity_search_with_score(query_content, k=5)
        response = {
            "ok": True,
            "data": docs_scores,
        }
    except Exception as e:
        logger.error(e)
        response = {"ok": False, "message": "查询失败"}
    finally:
        return response


def run_document_index_task(
    body,
    db,
):
    try:
        files_path = body.filesPath
        wiki_id = body.wikiId
        chunk_type = body.chunkType
        parent_chunk_size = body.parentChunkSize
        parent_chunk_overlap = body.parentChunkOverlap
        child_chunk_size = body.childChunkSize
        child_chunk_overlap = body.childChunkOverlap

        # 向量化处理
        qw_embedding = QWEmbeddings(
            api_key=settings.QIANWEN_API_KEY, model="text-embedding-v1"
        )
        vector_db_url = f"http://{settings.VECTOR_DB_HOST}:{settings.VECTOR_DB_PORT}"
        vs = Qdrant.from_existing_collection(
            embedding=qw_embedding,
            url=vector_db_url,
            collection_name="bichon",
            path=None,
        )
        all_parent_docs = []
        all_child_docs = []

        for file_path in files_path:
            # 创建文件索引任务
            doc_task = DocumentIndexTask(
                wiki_id=wiki_id,
                file_name=file_path,
                status=1,
                total_chunks=0,
                processed_chunks=0,
                current_phase=1,
                error_message=None,
            )
            db.add(doc_task)
            db.commit()
            db.refresh(doc_task)

            # 插入 Document
            try:
                docs = load_doc(file_path)
                new_doc = Document(
                    wiki_id=wiki_id,
                    source_uri=file_path,
                    title=Path(file_path).name,
                    status=1,
                    hash=file_hash(file_path),
                    extra_metadata={},
                )
                db.add(new_doc)
                db.flush()
                doc_id = new_doc.id

                match chunk_type:
                    case WikiChunkType.Classical.value:
                        split_docs = split_doc(
                            docs, parent_chunk_size, parent_chunk_overlap
                        )
                    case WikiChunkType.ParentChild.value:
                        doc_task.current_phase = 2
                        db.commit()
                        parent_chunks = []
                        child_chunks = []
                        parent_docs, child_docs = split_docs_with_parents(
                            docs,
                            parent_chunk_size,
                            parent_chunk_overlap,
                            child_chunk_size,
                            child_chunk_overlap,
                            return_parent_docs=True,
                        )
                        # ----- 写入 ParentChunk -----
                        # parent_key -> parent_chunk_id 映射
                        parent_id_to_chunk_id = {}
                        for p_doc in parent_docs:
                            parent_metadata = p_doc.metadata
                            print("metadata", parent_metadata)
                            parent_chunk_id = uuid.uuid4()
                            parent_id_to_chunk_id[parent_metadata["parent_id"]] = (
                                parent_chunk_id
                            )
                            parent_chunks.append(
                                {
                                    "id": parent_chunk_id,
                                    "wiki_id": wiki_id,
                                    "document_id": new_doc.id,
                                    "index": p_doc.metadata["parent_index"],
                                    "type": 1,
                                    "content": p_doc.page_content,
                                    "extra_metadata": parent_metadata,
                                }
                            )

                        for c_doc in child_docs:
                            child_metadata = c_doc.metadata
                            parent_id = child_metadata["parent_id"]
                            parent_chunk_id = parent_id_to_chunk_id.get(parent_id)
                            index_in_parent = child_metadata["index_in_parent"]

                            child_chunk_id = uuid.uuid4()
                            point_id = str(child_chunk_id)

                            child_chunks.append(
                                {
                                    "id": child_chunk_id,
                                    "parent_id": parent_chunk_id,
                                    "document_id": doc_id,
                                    "wiki_id": wiki_id,
                                    "index_in_parent": index_in_parent,
                                    "content": c_doc.page_content,
                                    "embedding_status": 1,
                                    "qdrant_point_id": point_id,
                                }
                            )
                            child_metadata.update(
                                {
                                    "child_chunk_id": str(child_chunk_id),
                                }
                            )
                            c_doc.metadata = child_metadata

                        # 更新总 child chunk 数
                        doc_task.total_chunks = len(child_docs)
                        doc_task.current_phase = 4
                        db.commit()

                        all_parent_docs.extend(parent_docs)
                        all_child_docs.extend(child_docs)
                        # 批量写入 PG
                        if parent_chunks:
                            db.execute(insert(ParentChunk), parent_chunks)
                        if child_chunks:
                            db.execute(insert(ChildChunk), child_chunks)
                        db.commit()
                        doc_task.current_phase = 8
                        db.commit()

                if chunk_type == WikiChunkType.ParentChild.value:
                    # 子块进向量数据库
                    if all_child_docs:
                        doc_task.current_phase = 8
                        db.commit()
                        BATCH_SIZE = 100
                        processed = 0

                        for i in range(0, len(child_docs), BATCH_SIZE):
                            batch = child_docs[i : i + BATCH_SIZE]

                            vs.add_documents(
                                documents=batch,
                                ids=[doc.metadata["child_chunk_id"] for doc in batch],
                            )

                            processed += len(batch)
                            doc_task.processed_chunks = processed
                            db.commit()

                        # 文件完成
                        doc_task.status = 2  # done
                        doc_task.current_phase = 16
                        db.commit()
            except Exception as e:
                doc_task.status = 4  # error
                doc_task.current_phase = "error"
                doc_task.error_message = str(e)
                db.commit()
    except Exception as e:
        raise
