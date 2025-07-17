from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from llm.qwen import ChatQW
from schemas.model import (
    ModelProviderAddRequest,
    ModelProviderQueryRequest,
    ModelProviderUpdateRequest,
)
from models import ModelProvider, get_db
from utils.logger import logger

router = APIRouter(prefix="/api/model-provider", tags=["ModelProvider"])


@router.post("/create-model-provider")
async def create_model_provider(
    body: ModelProviderAddRequest, db: Session = Depends(get_db)
):
    response = {}
    try:
        model_provider = (
            db.query(ModelProvider)
            .filter(ModelProvider.name == body.modelProviderName)
            .first()
        )
        if model_provider:
            response = {"ok": False, "message": "模型提供商已存在"}
            return response
        new_model_provider = ModelProvider(
            active=True,
            name=body.modelProviderName,
            desc=(body.modelProviderDesc if body.modelProviderDesc else ""),
        )
        db.add(new_model_provider)
        db.commit()
        response = {
            "ok": True,
            "message": "添加成功",
            "model_provider_id": new_model_provider.id,
        }
    except Exception as e:
        db.rollback()
        response = {"ok": False, "message": "模型提供商添加失败"}
        logger.error(e)
    finally:
        return response


@router.post("/find-model-provider")
async def find_model_provider(
    body: ModelProviderQueryRequest, db: Session = Depends(get_db)
):
    response = {}
    try:
        model_providers = (
            db.query(ModelProvider).options(joinedload(ModelProvider.models)).all()
        )
        response = {"ok": True, "data": model_providers}
    except Exception as e:
        db.rollback()
        response = {"ok": False, "message": "获取模型提供商失败"}
        logger.error(e)
    finally:
        return response


@router.post("/update-model-provider")
async def update_model_provider(
    body: ModelProviderUpdateRequest, db: Session = Depends(get_db)
):
    response = {}
    try:
        provider = (
            db.query(ModelProvider)
            .filter(ModelProvider.id == body.modelProviderId)
            .first()
        )
        if not provider:
            response = {"ok": False, "message": "模型提供商不存在"}
            return
        # 验证 api_key
        llm = ChatQW(api_key=body.modelProviderApiKey)
        if not llm.test_api_key():
            response = {"ok": False, "message": "API KEY 无效"}
            return
        provider.api_key = body.modelProviderApiKey
        db.commit()
        db.refresh(provider)

        response = {"ok": True, "data": "API KEY 更新成功"}
    except Exception as e:
        db.rollback()
        response = {"ok": False, "message": "获取模型提供商失败"}
        logger.error(e)
    finally:
        return response
