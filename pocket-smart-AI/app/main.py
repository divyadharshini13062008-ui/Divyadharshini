from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routes.auth import router as auth_router
from app.routes.pages import router as pages_router
from app.routes.planners import router as planners_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "Budget-aware AI planning assistant for "
        "home interiors, parties, and jewelry."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)


app.include_router(pages_router)
app.include_router(auth_router)
app.include_router(planners_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "application": settings.app_name,
        "environment": settings.environment,
    }