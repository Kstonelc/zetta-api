from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from llm.qwen import QWProvider
from schemas.model import (
    ModelProviderAddRequest,
    ModelProviderQueryRequest,
    ModelProviderUpdateRequest,
)
from utils.common import encrypt_api_key
from utils.jwt import verify_token
from models import ModelProvider, Model, get_db
from enums import ModelProviderUpdateType
from utils.logger import logger

router = APIRouter(prefix="/api/model-provider", tags=["ModelProvider"])


@router.post("/create-model-provider")
async def create_model_provider(
    body: ModelProviderAddRequest,
    db: Session = Depends(get_db),
    token=Depends(verify_token),
):
    response = {}
    try:
        model_provider_name = body.modelProviderName
        model_provider_desc = body.modelProviderDesc if body.modelProviderDesc else ""

        model_provider = (
            db.query(ModelProvider)
            .filter(ModelProvider.name == model_provider_name)
            .first()
        )
        if model_provider:
            response = {"ok": False, "message": "模型提供商已存在"}
            return response
        new_model_provider = ModelProvider(
            active=True,
            name=model_provider_name,
            desc=model_provider_desc,
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
    body: ModelProviderQueryRequest,
    db: Session = Depends(get_db),
    # 加上表示验证token合法
    token=Depends(verify_token),
):
    response = {}
    try:
        model_providers = (
            db.query(ModelProvider)
            .options(joinedload(ModelProvider.models))
            .filter(ModelProvider.active.is_(True))
            .all()
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
    body: ModelProviderUpdateRequest,
    db: Session = Depends(get_db),
    token=Depends(verify_token),
):
    response = {}
    try:
        model_provider_id = body.modelProviderId
        model_provider_api_key = body.modelProviderApiKey
        model_provider_update_type = body.modelProviderUpdateType

        provider = (
            db.query(ModelProvider)
            .filter(ModelProvider.id == model_provider_id)
            .first()
        )
        if not provider:
            response = {"ok": False, "message": "模型提供商不存在"}
            return

        # 验证 api_key
        if not model_provider_update_type == ModelProviderUpdateType.Clear:
            llm = QWProvider(api_key=model_provider_api_key)
            if not llm.test_api_key():
                response = {"ok": False, "message": "API KEY 无效"}
                return
        provider.api_key = encrypt_api_key(model_provider_api_key)
        db.commit()
        db.refresh(provider)

        response = {
            "ok": True,
            "data": (
                "API KEY 更新成功"
                if model_provider_update_type == ModelProviderUpdateType.Update
                else "移除API KEY成功"
            ),
        }
    except Exception as e:
        db.rollback()
        response = {"ok": False, "message": "更新模型提供商失败"}
        logger.error(e)
    finally:
        return response


@router.post("/find-models")
async def find_models(
    body: ModelProviderQueryRequest,
    db: Session = Depends(get_db),
    token=Depends(verify_token),
):
    response = {}
    try:
        model_provider_id = body.modelProviderId

        models = (
            db.query(Model).filter(Model.model_provider_id == model_provider_id).all()
        )
        response = {
            "ok": True,
            "data": models,
            "message": "获取模型成功",
        }
    except Exception as e:
        print(e)
        response = {"ok": False, "message": "获取模型失败"}
        logger.error(e)
    finally:
        return response
