from fastapi import FastAPI
from controllers import user

app = FastAPI(title="Zetta API")

# 注册路由
app.include_router(user.router)
