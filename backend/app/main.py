import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import CORS_ORIGINS, UPLOADS_DIR
from .database import create_db_and_tables
from .routers import auth, posts


# El setup corre al arrancar el servidor, no al importar el módulo:
# los tests pueden importar la app sin tocar la base real.
@asynccontextmanager
async def lifespan(_app: FastAPI):
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    create_db_and_tables()
    yield


app = FastAPI(title="Minigram API", version="0.2.0", lifespan=lifespan)

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
