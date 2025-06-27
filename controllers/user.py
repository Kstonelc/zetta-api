from fastapi import APIRouter


router = APIRouter(prefix="/user", tags=["User"])


@router.get("/find-user")
async def find_user():
    return {
        "ok": True,
        "message": "用户查找成功",
        "data": {"id": 1, "name": "John Doe"},
    }
