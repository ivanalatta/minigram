import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import UPLOADS_DIR
from .database import create_db_and_tables
from .routers import auth, posts

os.makedirs(UPLOADS_DIR, exist_ok=True)
create_db_and_tables()

app = FastAPI(title="Minigram API", version="0.2.0")

# El frontend (Vite) corre en el puerto 5173 en desarrollo.
# Sin esto, el navegador bloquea las llamadas del frontend al backend (CORS).
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(posts.router)

# Las imágenes subidas se sirven como archivos estáticos en /uploads/...
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


@app.get("/health")
def health_check():
    """Endpoint de verificación: confirma que la API está viva."""
    return {"status": "ok", "service": "minigram-api"}
