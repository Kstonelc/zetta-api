from fastapi import APIRouter
from config import settings

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/find-user")
async def find_user():
    print(settings.QIANWEN_API_KEY)
    return {
        "ok": True,
        "message": "用户查找成功",
        "data": {"id": 1, "name": "John Doe"},
    }
