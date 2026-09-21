import os

from dotenv import load_dotenv

load_dotenv()

# Configuración por variables de entorno con valores por defecto para desarrollo.
# En producción, SECRET_KEY y DATABASE_URL se definen en el .env del servidor.
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-cambiar-en-produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 día

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./minigram.db")

UPLOADS_DIR = "uploads"

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
