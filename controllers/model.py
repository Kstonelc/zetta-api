from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.model import (
    ModelAddRequest,
    ModelQueryRequest,
    ModelUpdateRequest,
)
from models import Model, get_db
from utils.logger import logger

router = APIRouter(prefix="/api/model", tags=["Model"])


@router.post("/create-model")
async def create_model(body: ModelAddRequest, db: Session = Depends(get_db)):
    response = {}
    try:
        model_name = body.modelName
        model_display_name = body.modelDisplayName if body.modelDisplayName else None
        model_provider_id = body.modelProviderId
        model_max_context_tokens = (
            body.modelMaxContextTokens if body.modelMaxContextTokens else None
        )
        model_token_limit = body.modelTokenLimit if body.modelTokenLimit else None

        model = db.query(Model).filter(Model.name == model_name).first()
        if model:
            response = {"ok": False, "message": "模型已存在"}
            return
        new_model = Model(
            active=True,
            name=model_name,
            display_name=model_display_name,
            model_provider_id=model_provider_id,
            max_context_tokens=model_max_context_tokens,
            token_limit=model_token_limit,
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


@router.post("/find-models")
async def find_models(body: ModelQueryRequest, db: Session = Depends(get_db)):
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
        db.rollback()
        response = {"ok": False, "message": "获取模型失败"}
        logger.error(e)
    finally:
        return response


@router.post("/update-model")
async def update_model(body: ModelUpdateRequest, db: Session = Depends(get_db)):
    response = {}
    try:
        modelId = body.modelId
        active = body.active

        model = db.query(Model).filter(Model.id == modelId).first()
        if not model:
            response = {"ok": False, "message": "模型不存在"}
            return
        if active is not None:
            model.active = active

        db.commit()
        response = {
            "ok": True,
            "message": "更新模型成功",
        }

    except Exception as e:
        db.rollback()
        response = {"ok": False, "message": "更新模型失败"}
        logger.error(e)
    finally:
        return response
