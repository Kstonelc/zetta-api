from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from utils.logger import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        log_info = f"➡️ {request.method} {request.url.path}"
        # 请求日志
        if request.query_params:
            log_info += f" Query Params:{request.query_params} |"
        try:
            body = await request.body()
            if body:
                body = body.decode("utf-8")
                log_info += f" Request Body:{body}"
        except Exception:
            pass

        # 仅限开发环境使用
        logger.info(log_info)

        response = await call_next(request)

        # 响应日志
        logger.info(f"⬅️ {request.method} {request.url.path} -> {response.status_code}")
        return response


# JWT 认证
