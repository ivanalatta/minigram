FROM python:3.14-slim

WORKDIR /code

# Copiamos primero requirements.txt para aprovechar la caché de Docker:
# si el código cambia pero las dependencias no, no se reinstalan.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
