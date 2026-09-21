from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Minigram API", version="0.1.0")

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


@app.get("/health")
def health_check():
    """Endpoint de verificación: confirma que la API está viva."""
    return {"status": "ok", "service": "minigram-api"}
