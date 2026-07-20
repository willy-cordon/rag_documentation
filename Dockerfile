# Imagen pequeña con la versión de Python soportada por la aplicación.
FROM python:3.12-slim

# Evita archivos .pyc y fuerza logs visibles inmediatamente en Docker.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Todos los comandos siguientes se ejecutan desde la raíz de la aplicación.
WORKDIR /app

# Se copian primero las dependencias para aprovechar la caché de Docker.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# La aplicación y el manual se incluyen dentro de la imagen.
COPY app ./app
COPY documents ./documents

# Puerto HTTP expuesto por Uvicorn.
EXPOSE 8000

# Arranque de la API accesible desde fuera del contenedor.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
