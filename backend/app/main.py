import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import CORS_ORIGINS, UPLOADS_DIR
from .database import create_db_and_tables
from .routers import auth, posts

os.makedirs(UPLOADS_DIR, exist_ok=True)
create_db_and_tables()

app = FastAPI(title="Minigram API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(posts.router)

app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "minigram-api"}
