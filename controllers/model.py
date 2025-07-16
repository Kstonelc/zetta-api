from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.model import ModelProviderAddRequest, ModelAddRequest
from models import ModelProvider, Model, get_db
from utils.logger import logger

router = APIRouter(prefix="/api/model", tags=["Model"])


@router.post("/create-model-provider")
async def create_model_provider(
    model_provider_info: ModelProviderAddRequest, db: Session = Depends(get_db)
):
    response = {}
    try:
        model_provider = (
            db.query(ModelProvider)
            .filter(ModelProvider.name == model_provider_info.modelProviderName)
            .first()
        )
        if model_provider:
            response = {"ok": False, "message": "模型提供商已存在"}
            return response
        new_model_provider = ModelProvider(
            active=True,
            name=model_provider_info.modelProviderName,
            desc=(
                model_provider_info.modelProviderDesc
                if model_provider_info.modelProviderDesc
                else ""
            ),
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


@router.post("/create-model")
async def create_model(model_info: ModelAddRequest, db: Session = Depends(get_db)):
    response = {}
    try:
        model = db.query(Model).filter(Model.name == model_info.modelName).first()
        if model:
            response = {"ok": False, "message": "模型已存在"}
            return
        new_model = Model(
            active=True,
            name=model_info.modelName,
            display_name=(
                model_info.modelDisplayName if model_info.modelDisplayName else None
            ),
            provider_id=model_info.modelProviderId,
            api_key=model_info.apiKey if model_info.modelApiKey else None,
            max_context_tokens=(
                model_info.modelMaxContextTokens
                if model_info.modelMaxContextTokens
                else None
            ),
            token_limit=(
                model_info.modelTokenLimit if model_info.modelTokenLimit else None
            ),
        )
        db.add(new_model)
        db.commit()
        response = {
            "ok": True,
            "message": "模型添加成功",
            "model_id": new_model.id,
        }
    except Exception as e:
        db.rollback()
        response = {"ok": False, "message": "模型添加失败"}
        logger.error(e)
    finally:
        return response
