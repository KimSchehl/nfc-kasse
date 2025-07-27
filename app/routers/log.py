from fastapi import APIRouter, Request
from app.utils.logger import log

router = APIRouter(prefix="/log", tags=["log"])

@router.post("/")
async def frontend_log(request: Request):
    data = await request.json()
    log(f"Frontend: {data.get('message')}", user=data.get('user'))
    return {"success": True}