from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_401_UNAUTHORIZED
from contextlib import asynccontextmanager
import uvicorn
from controllers import test, user, model, model_provider, tenant, wiki
from middlewares import RequestLoggingMiddleware
from fastapi.middleware.cors import CORSMiddleware
from utils.vector_db import vector_client
from exceptions import AuthTokenException
from models.db import engine
from utils.logger import logger


# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    check_db_connection()
    check_vectordb_connection()

    yield  # 资源释放等后续操作


def check_db_connection():
    try:
        engine.connect()
        logger.info("[DB]: ✅ DB Connection Success")
    except Exception as e:
        logger.error(f"[DB]: ❌ DB Connection Failed: {e}")
        raise RuntimeError("DB Connect Failed") from e


def check_vectordb_connection():
    try:
        vector_client.ping()
        logger.info("[Qdrant]: ✅ Qdrant Connection Success")
    except Exception as e:
        logger.error(f"[Qdrant]: ❌ Qdrant Connection Failed: {e}")
        raise RuntimeError("Qdrant Connect Failed") from e


app = FastAPI(lifespan=lifespan)


# 注册中间件
app.add_middleware(RequestLoggingMiddleware)
# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ 允许所有 origin
    allow_credentials=False,  # ⚠️ 必须为 False，不能和 "*" 同时使用
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 routers
app.include_router(user.router)
app.include_router(test.router)
app.include_router(model.router)
app.include_router(model_provider.router)
app.include_router(tenant.router)
app.include_router(wiki.router)


# 参数校验处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # 422 status_code 参数校验失败
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"ok": False, "message": "请求参数不合法", "errors": exc.errors()},
    )


# 全局异常处理
@app.exception_handler(AuthTokenException)
async def auth_token_exception_handler(request: Request, exc: AuthTokenException):
    return JSONResponse(
        status_code=HTTP_401_UNAUTHORIZED,
        content={"ok": False, "message": exc.detail},
    )


if __name__ == "__main__":
    logger.info("✅ Zetta Server Start")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
