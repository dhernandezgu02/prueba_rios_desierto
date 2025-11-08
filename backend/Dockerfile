# Dockerfile para Backend - Sistema de Gestión de Clientes Falabella
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema (SQLite3 ya viene incluido)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN groupadd -r django && useradd -r -g django django

# Crear directorio de trabajo
WORKDIR /app

# Copiar e instalar dependencias Python
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install gunicorn

# Copiar código fuente
COPY . /app/

# Crear directorio para base de datos SQLite
RUN mkdir -p /app/data

# Crear directorio para archivos estáticos
RUN mkdir -p /app/staticfiles

# Cambiar permisos al usuario django
RUN chown -R django:django /app

# Hacer ejecutable el script de inicio
RUN chmod +x /app/start.sh

# Cambiar al usuario no-root
USER django

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["/app/start.sh"]