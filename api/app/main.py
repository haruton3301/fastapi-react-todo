from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth as auth_router
from app.routers import status as status_router
from app.routers import task as task_router

app = FastAPI(
    title="Task Management API",
    description="FastAPI + React Todo App",
    version="0.1.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(auth_router.router)
app.include_router(status_router.router)
app.include_router(task_router.router)
