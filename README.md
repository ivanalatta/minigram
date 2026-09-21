# Minigram

Clon simplificado de Instagram: usuarios pueden registrarse, iniciar sesión,
publicar posts, dar likes y comentar.

## Stack

| Capa      | Tecnología                  | Por qué                                              |
|-----------|-----------------------------|------------------------------------------------------|
| Frontend  | React 19 + Vite             | Estándar actual para SPAs; Vite es el tooling oficial recomendado |
| Backend   | FastAPI (Python)            | API rápida de construir, validación automática y documentación Swagger incluida |
| Base de datos | PostgreSQL (SQLite en desarrollo) | Postgres en producción; SQLite simplifica el desarrollo local |
| Auth      | OAuth2 + JWT                | Flujo estándar de FastAPI (`OAuth2PasswordBearer`)   |
| Deploy    | Docker Compose en Digital Ocean + Nginx + Certbot | Un solo comando levanta todo el stack |

## Desarrollo local

Requisitos: Node 22+, Python 3.12+.

**Backend** (puerto 8000):

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows  |  source .venv/bin/activate en Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Documentación interactiva del API: http://localhost:8000/docs

**Frontend** (puerto 5173):

```bash
cd frontend
npm install
npm run dev
```

Abrir http://localhost:5173.

### Login con Google (opcional en desarrollo)

1. En [Google Cloud Console](https://console.cloud.google.com) → APIs & Services →
   Credentials → Create Credentials → **OAuth client ID**, tipo "Web application".
2. Agregar `http://localhost:5173` en "Authorized JavaScript origins".
3. Copiar el client ID en `frontend/.env` (`VITE_GOOGLE_CLIENT_ID`) y en
   `backend/.env` (`GOOGLE_CLIENT_ID`) — hay un `.env.example` en cada carpeta.

Si no está configurado, el botón de Google no se muestra y el resto de la app
funciona normal.

## Producción

```bash
cp .env.example .env   # y completar los valores
docker compose up -d --build
```

## Estado del proyecto

- [x] Fase 0 — Esqueleto: frontend + backend conectados, Docker listo
- [x] Fase 1 — Backend: modelos, auth JWT, endpoints de posts/likes/comentarios
- [x] Fase 2 — Frontend: login, feed, crear post
- [x] Fase 3 — Login con Google (OAuth)
- [ ] Fase 4 — Deploy en Digital Ocean + dominio + HTTPS
