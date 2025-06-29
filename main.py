from fastapi import FastAPI
import uvicorn
from controllers import user, ai_test
from middlewares import RequestLoggingMiddleware
from loguru import logger

app = FastAPI()

# 注册中间件
app.add_middleware(RequestLoggingMiddleware)


# 注册 routers
app.include_router(user.router)
app.include_router(ai_test.router)


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
