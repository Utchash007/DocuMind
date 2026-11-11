"""DocuMind v2 application: owned resources and public liveness."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import load_application_env

load_application_env()

from app.api.conversations import router as conversations_router
from app.api.documents import router as documents_router
from app.api.messages import router as messages_router
from app.api.projects import router as projects_router
from app.api.users import router as users_router

app = FastAPI(title="DocuMind Backend", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
        ).split(",")
        if origin.strip()
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(projects_router)
app.include_router(documents_router)
app.include_router(conversations_router)
app.include_router(messages_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to DocuMind API"}


@app.get("/health")
def health_check() -> dict[str, object]:
    return {
        "status": "healthy",
        "config": {
            "groq_api_key_loaded": bool(os.getenv("GROQ_API_KEY")),
            "chroma_host_loaded": bool(os.getenv("CHROMA_HOST")),
        },
    }
