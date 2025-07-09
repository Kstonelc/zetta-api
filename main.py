from fastapi import FastAPI
import uvicorn
from controllers import user, ai_test
from middlewares import RequestLoggingMiddleware
import utils.chroma as chroma_client
from loguru import logger

app = FastAPI()

# 注册中间件
app.add_middleware(RequestLoggingMiddleware)


# 注册 routers
app.include_router(user.router)
app.include_router(ai_test.router)


@app.on_event("startup")
def check_chroma_connection():
    if not chroma_client.ping():
        raise RuntimeError("❌ Chroma 向量数据库连接失败，应用启动中止")
    print("✅ 成功连接 Chroma 向量数据库")


if __name__ == "__main__":
    logger.info("Zetta Server Start")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None,
        log_level="debug",
    )
