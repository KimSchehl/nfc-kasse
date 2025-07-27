from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/static-redirects", tags=["static-redirects"])

@router.get("/login")
async def login_redirect():
    return RedirectResponse("/login.html")

# Hier kannst du weitere Weiterleitungen ergänzen, z.B.:
# @router.get("/impressum")
# async def impressum_redirect():
#     return RedirectResponse("/impressum.html")