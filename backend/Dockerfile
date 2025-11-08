# Dockerfile para Backend - Sistema Ríos del Desierto
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN groupadd -r django && useradd -r -g django django

# Crear directorio de trabajo
WORKDIR /app

# Copiar e instalar dependencias Python
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install psycopg2-binary gunicorn

# Copiar código fuente
COPY . /app/

# Crear directorio para archivos estáticos
RUN mkdir -p /app/staticfiles

# Cambiar permisos al usuario django
RUN chown -R django:django /app

# Cambiar al usuario no-root
USER django

# Recopilar archivos estáticos
RUN python manage.py collectstatic --noinput --clear

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "30", "wsgi:application"]