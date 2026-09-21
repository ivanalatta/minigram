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

### Tests

```bash
# Backend (desde backend/, con el venv activado)
pip install -r requirements-dev.txt
pytest

# Frontend (desde frontend/)
npm test
```

### Login con Google (opcional en desarrollo)

1. En [Google Cloud Console](https://console.cloud.google.com) → APIs & Services →
   Credentials → Create Credentials → **OAuth client ID**, tipo "Web application".
2. Agregar `http://localhost:5173` en "Authorized JavaScript origins".
3. Copiar el client ID en `frontend/.env` (`VITE_GOOGLE_CLIENT_ID`) y en
   `backend/.env` (`GOOGLE_CLIENT_ID`) — hay un `.env.example` en cada carpeta.

Si no está configurado, el botón de Google no se muestra y el resto de la app
funciona normal.

## Producción (Digital Ocean)

Arquitectura: un droplet corre todo con Docker Compose. Nginx (contenedor del
frontend) sirve la app en HTTPS y hace de reverse proxy hacia el backend, así
API y frontend comparten dominio (sin CORS). Postgres y las imágenes subidas
persisten en volúmenes de Docker.

**1. Preparar el servidor** (una sola vez)

- Crear un droplet Ubuntu en Digital Ocean (el básico alcanza) e instalar
  Docker: https://docs.docker.com/engine/install/ubuntu/
- Apuntar el dominio al droplet: un registro DNS tipo A con la IP pública.
- Clonar el repo y configurar:

```bash
git clone <url-del-repo> && cd minigram
cp .env.example .env   # completar DOMAIN, POSTGRES_PASSWORD, SECRET_KEY...
```

**2. Emitir el certificado HTTPS** (una sola vez, con el puerto 80 libre)

```bash
docker compose run --rm -p 80:80 certbot certonly --standalone \
  -d $(grep ^DOMAIN .env | cut -d= -f2) \
  --agree-tos --register-unsafely-without-email
```

**3. Levantar todo**

```bash
docker compose up -d --build
```

**Renovar el certificado** (Let's Encrypt dura 90 días; correr cada ~2 meses
o programarlo con cron):

```bash
docker compose run --rm certbot renew --webroot -w /var/www/certbot
docker compose exec frontend nginx -s reload
```

**Actualizar la app** tras un `git pull`: `docker compose up -d --build`.

Nota: para que el login con Google funcione en producción hay que agregar
`https://<dominio>` en los "Authorized JavaScript origins" del client ID.

## Estado del proyecto

- [x] Fase 0 — Esqueleto: frontend + backend conectados, Docker listo
- [x] Fase 1 — Backend: modelos, auth JWT, endpoints de posts/likes/comentarios
- [x] Fase 2 — Frontend: login, feed, crear post
- [x] Fase 3 — Login con Google (OAuth)
- [ ] Fase 4 — Deploy en Digital Ocean + dominio + HTTPS
