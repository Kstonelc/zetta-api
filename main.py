from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from controllers import user, ai_test
from middlewares import RequestLoggingMiddleware
from utils.chroma import chroma_client
from models.db import check_db_connection
from utils.logger import logger

app = FastAPI()

# 注册中间件
app.add_middleware(RequestLoggingMiddleware)


# 注册 routers
app.include_router(user.router)
app.include_router(ai_test.router)


# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        check_db_connection()
        logger.success("✅ 数据库连接成功")
        check_chroma_connection()
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        raise RuntimeError("数据库连接失败") from e

    yield
    logger.info("❌ 应用即将关闭")


def check_chroma_connection():
    if not chroma_client.ping():
        logger.error("[Chroma]: ❌ChromaDB Connection Failed")
    logger.info("[Chroma]: ✅ChromaDB Connection Success")


if __name__ == "__main__":
    logger.info("✅Zetta Server Start")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None,
        log_level="debug",
    )
