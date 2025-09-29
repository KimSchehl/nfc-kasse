from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, static_redirects, categories, products, settings, transactions, user, log, finances
from fastapi.responses import RedirectResponse


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router, prefix="/api")
app.include_router(static_redirects.router)
app.include_router(categories.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(log.router, prefix="/api")
app.include_router(finances.router, prefix="/api")

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

