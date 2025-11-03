from fastapi import APIRouter, Depends
from sqlalchemy import any_, and_
from sqlalchemy.orm import Session, joinedload
from schemas.model import (
    ModelCreateRequest,
    ModelUpdateRequest,
    ModelQueryRequest,
)
from models import Model, ModelProvider, Tenant, get_db
from utils.jwt import verify_token
from utils.logger import logger

router = APIRouter(prefix="/api/model", tags=["Model"])


@router.post("/create-model")
async def create_model(
    body: ModelCreateRequest,
    db: Session = Depends(get_db),
    token=Depends(verify_token),
):
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


@router.post("/update-model")
async def update_model(
    body: ModelUpdateRequest,
    db: Session = Depends(get_db),
    token=Depends(verify_token),
):
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


@router.post("/find-models")
async def find_models(
    body: ModelQueryRequest, db: Session = Depends(get_db), token=Depends(verify_token)
):
    response = {}
    try:
        model_type = body.modelType
        tenant_id = body.tenantId

        filters = [Model.active.is_(True), model_type.value == any_(Model.types)]
        if tenant_id is not None:
            filters.append(Tenant.id == tenant_id)

        models = (
            db.query(Model)
            .options(joinedload(Model.provider))
            .join(Model.provider)
            .join(ModelProvider.tenants)
            .filter(and_(*filters))
            .all()
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
