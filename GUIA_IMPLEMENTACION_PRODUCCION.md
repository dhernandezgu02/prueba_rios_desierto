# 🚀 Guía de Implementación en Ambiente Productivo
## Sistema de Gestión de Clientes - Ríos del Desierto

---

## 📋 Información del Sistema

**Tecnologías:**
- Backend: Django 5.0.6 + Django REST Framework
- Frontend: React 18+ con TypeScript
- Base de Datos: PostgreSQL (producción)
- Containerización: Docker + Docker Compose
- Nube: **Google Cloud Platform (GCP)**

---

## 🐳 DESPLIEGUE CON DOCKER

### Requisitos
- Docker & Docker Compose instalados
- Git
- Cuenta de Google Cloud Platform

### Ejecución Local
```bash
# Clonar repositorio
git clone https://github.com/dhernandezgu02/prueba_rios_desierto.git
cd rios-desierto

# Construir y ejecutar
docker-compose up --build -d

# Verificar
docker-compose ps
docker-compose logs -f

# Acceder:
# Frontend: http://localhost:3000
# API: http://localhost:8001/api/
# Base de datos: localhost:5432
```

---

## ☁️ DESPLIEGUE EN GOOGLE CLOUD

### 1. Configuración Inicial
```bash
# Instalar Google Cloud CLI
curl https://sdk.cloud.google.com | bash

# Configurar proyecto
gcloud auth login
gcloud config set project TU_PROJECT_ID
```

### 2. Crear Base de Datos
```bash
# Crear instancia Cloud SQL
gcloud sql instances create rios-db-prod \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1

# Crear base de datos
gcloud sql databases create rios_desierto_db \
    --instance=rios-db-prod

# Crear usuario
gcloud sql users create rios_user \
    --instance=rios-db-prod \
    --password=TU_PASSWORD_SEGURO
```

### 3. Desplegar Backend
```bash
gcloud run deploy rios-backend \
    --source=./backend \
    --region=us-central1 \
    --allow-unauthenticated \
    --set-env-vars="DEBUG=False" \
    --set-env-vars="DB_HOST=/cloudsql/TU_PROJECT_ID:us-central1:rios-db-prod" \
    --set-env-vars="DB_NAME=rios_desierto_db" \
    --set-env-vars="DB_USER=rios_user" \
    --set-env-vars="DB_PASSWORD=TU_PASSWORD_SEGURO" \
    --add-cloudsql-instances=TU_PROJECT_ID:us-central1:rios-db-prod
```

### 4. Desplegar Frontend
```bash
# Obtener URL del backend
BACKEND_URL=$(gcloud run services describe rios-backend --region=us-central1 --format="value(status.url)")

# Desplegar frontend
gcloud run deploy rios-frontend \
    --source=./frontend \
    --region=us-central1 \
    --allow-unauthenticated \
    --set-env-vars="REACT_APP_API_BASE_URL=${BACKEND_URL}/api"
```

### 5. CI/CD Automático
```bash
# Configurar build automático
gcloud builds submit --config=cloudbuild.yaml

# Crear trigger desde repositorio
gcloud builds triggers create github \
    --repo-name=rios-desierto \
    --repo-owner=TU_GITHUB_USER \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml
```

---

## 🛠️ COMANDOS ÚTILES

### Docker Local
```bash
# Ejecutar migraciones
docker-compose exec backend python manage.py migrate

# Crear superusuario
docker-compose exec backend python manage.py createsuperuser

# Ver logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Backup de base de datos
docker-compose exec db pg_dump -U rios_user rios_desierto_db > backup.sql
```

### Google Cloud
```bash
# Ver servicios desplegados
gcloud run services list --region=us-central1

# Obtener URLs
gcloud run services describe rios-backend --region=us-central1 --format="value(status.url)"
gcloud run services describe rios-frontend --region=us-central1 --format="value(status.url)"

# Ver logs en tiempo real
gcloud run logs tail --service=rios-backend --region=us-central1

# Conectar a base de datos
gcloud sql connect rios-db-prod --user=rios_user
```

---

## 📊 ESTRUCTURA DEL PROYECTO

```
rios-desierto/
├── backend/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── cloudbuild.yaml
```

---

## � COSTOS ESTIMADOS GCP

- **Cloud Run:** $10-40 USD/mes
- **Cloud SQL:** $15-50 USD/mes
- **Cloud Build:** $0-10 USD/mes
- **Total:** $25-100 USD/mes

---

## 🔗 URLs DE ACCESO

### Local (Docker)
- Frontend: http://localhost:3000
- API: http://localhost:8001/api/
- Admin: http://localhost:8001/admin/

### Google Cloud (dinámicas)
```bash
BACKEND=$(gcloud run services describe rios-backend --region=us-central1 --format="value(status.url)")
FRONTEND=$(gcloud run services describe rios-frontend --region=us-central1 --format="value(status.url)")
echo "Frontend: $FRONTEND"
echo "API: $BACKEND/api/"
```

---

**Sistema listo para producción con Docker y Google Cloud Platform**

## 🔧 Requisitos del Servidor

### Especificaciones Mínimas
- **CPU:** 2 cores
- **RAM:** 4GB
- **Disco:** 50GB SSD
- **Red:** 100 Mbps

### Especificaciones Recomendadas
- **CPU:** 4 cores
- **RAM:** 8GB
- **Disco:** 100GB SSD
- **Red:** 1 Gbps

---

## 📦 PASO 1: Preparación del Servidor

### 1.1 Actualizar el Sistema
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 Instalar Dependencias Base
```bash
sudo apt install python3 python3-pip python3-venv -y

curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

sudo apt install postgresql postgresql-contrib -y

sudo apt install nginx -y

sudo apt install git -y

sudo apt install htop curl wget unzip -y
```

---

## 🗄️ PASO 2: Configuración de Base de Datos

### 2.1 Configurar PostgreSQL
```bash
sudo -u postgres psql

CREATE DATABASE rios_desierto_db;
CREATE USER rios_user WITH PASSWORD '';
ALTER ROLE rios_user SET client_encoding TO 'utf8';
ALTER ROLE rios_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE rios_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE rios_desierto_db TO rios_user;
\q
```


## 🔙 PASO 3: Configuración del Backend

### 3.1 Crear Usuario de Sistema
```bash
sudo adduser --system --group --home /var/www/rios_desierto rios_app
```

### 3.2 Clonar/Subir el Código
```bash
sudo -u rios_app git clone https://github.com/dhernandezgu02/prueba_rios_desierto.git /var/www/rios_desierto/

sudo mkdir -p /var/www/rios_desierto/
sudo chown rios_app:rios_app /var/www/rios_desierto/
```

### 3.3 Configurar Entorno Virtual Python
```bash
sudo -u rios_app python3 -m venv /var/www/rios_desierto/backend/venv
sudo -u rios_app /var/www/rios_desierto/backend/venv/bin/pip install --upgrade pip
```

### 3.4 Instalar Dependencias Python
```bash
cd /var/www/rios_desierto/backend/
sudo -u rios_app ./venv/bin/pip install -r requirements.txt

sudo -u rios_app ./venv/bin/pip install gunicorn psycopg2-binary whitenoise
```

### 3.5 Configurar Variables de Entorno
```bash
sudo -u rios_app nano /var/www/rios_desierto/backend/.env
```

Contenido del archivo `.env`:
```env
# Configuración de Producción
DEBUG=False
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura_aqui
ALLOWED_HOSTS=tu_dominio.com,www.tu_dominio.com,tu_ip_servidor

# Base de Datos PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=rios_desierto_db
DB_USER=rios_user
DB_PASSWORD=tu_password_seguro
DB_HOST=localhost
DB_PORT=5432

# CORS (para React)
CORS_ALLOWED_ORIGINS=https://tu_dominio.com,https://www.tu_dominio.com

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_password_email
```

### 3.6 Actualizar settings.py para Producción
Agregar al final de `settings.py`:
```python

if not DEBUG:

    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # Configuración de seguridad
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 86400
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # En producción con HTTPS, habilitar:
    # SECURE_SSL_REDIRECT = True
    # SESSION_COOKIE_SECURE = True
    # CSRF_COOKIE_SECURE = True
```

### 3.7 Ejecutar Migraciones
```bash
cd /var/www/rios_desierto/backend/
sudo -u rios_app ./venv/bin/python manage.py migrate
sudo -u rios_app ./venv/bin/python manage.py collectstatic --noinput
```

### 3.8 Crear Superusuario
```bash
sudo -u rios_app ./venv/bin/python manage.py createsuperuser
```

---

## 🎨 PASO 4: Configuración del Frontend

### 4.1 Instalar Dependencias Node.js
```bash
cd /var/www/rios_desierto/frontend/
sudo -u rios_app npm install
```

### 4.2 Configurar Variables de Entorno del Frontend
```bash
sudo -u rios_app nano /var/www/rios_desierto/frontend/.env.production
```

Contenido:
```env
REACT_APP_API_BASE_URL=https://tu_dominio.com/api
GENERATE_SOURCEMAP=false
```

### 4.3 Construir para Producción
```bash
cd /var/www/rios_desierto/frontend/
sudo -u rios_app npm run build
```

---

## 🔧 PASO 5: Configuración de Gunicorn

### 5.1 Crear Archivo de Configuración Gunicorn
```bash
sudo nano /var/www/rios_desierto/backend/gunicorn.conf.py
```

Contenido:
```python
bind = "127.0.0.1:8001"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 5
preload_app = True
daemon = False
user = "rios_app"
group = "rios_app"
errorlog = "/var/log/gunicorn/error.log"
accesslog = "/var/log/gunicorn/access.log"
loglevel = "info"
```

### 5.2 Crear Directorios de Logs
```bash
sudo mkdir -p /var/log/gunicorn/
sudo chown rios_app:rios_app /var/log/gunicorn/
```

### 5.3 Crear Servicio Systemd para Gunicorn
```bash
sudo nano /etc/systemd/system/rios-desierto.service
```

Contenido:
```ini
[Unit]
Description=Gunicorn instance to serve Ríos del Desierto
After=network.target

[Service]
User=rios_app
Group=rios_app
WorkingDirectory=/var/www/rios_desierto/backend
Environment="PATH=/var/www/rios_desierto/backend/venv/bin"
ExecStart=/var/www/rios_desierto/backend/venv/bin/gunicorn --config gunicorn.conf.py wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### 5.4 Habilitar y Iniciar el Servicio
```bash
sudo systemctl daemon-reload
sudo systemctl enable rios-desierto
sudo systemctl start rios-desierto
sudo systemctl status rios-desierto
```

---

## 🌐 PASO 6: Configuración de Nginx

### 6.1 Crear Configuración de Nginx
```bash
sudo nano /etc/nginx/sites-available/rios-desierto
```

Contenido:
```nginx
server {
    listen 80;
    server_name tu_dominio.com www.tu_dominio.com;
    
    # Redirigir HTTP a HTTPS (después de configurar SSL)
    # return 301 https://$server_name$request_uri;
    
    # Configuración temporal para HTTP
    client_max_body_size 100M;
    
    # Servir archivos estáticos del Frontend (React)
    location / {
        root /var/www/rios_desierto/frontend/build;
        try_files $uri $uri/ /index.html;
        
        # Headers de cache para archivos estáticos
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Proxy para API del Backend (Django)
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
    
    # Servir archivos estáticos de Django (admin, DRF)
    location /static/ {
        alias /var/www/rios_desierto/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Servir archivos de media (uploads)
    location /media/ {
        alias /var/www/rios_desierto/backend/media/;
    }
    
    # Logs
    access_log /var/log/nginx/rios_desierto_access.log;
    error_log /var/log/nginx/rios_desierto_error.log;
}
```

### 6.2 Habilitar el Sitio
```bash
sudo ln -s /etc/nginx/sites-available/rios-desierto /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 PASO 7: Configuración SSL/HTTPS

### 7.1 Instalar Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 7.2 Obtener Certificado SSL
```bash
sudo certbot --nginx -d tu_dominio.com -d www.tu_dominio.com
```

### 7.3 Configurar Renovación Automática
```bash
sudo crontab -e
```

Agregar:
```cron
# Renovar certificados SSL automáticamente
0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx
```

---

## 🔥 PASO 8: Configuración del Firewall

### 8.1 Configurar UFW
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
sudo ufw status
```

---

## 📊 PASO 9: Configuración de Logs y Monitoreo

### 9.1 Configurar Logrotate
```bash
sudo nano /etc/logrotate.d/rios-desierto
```

Contenido:
```
/var/log/gunicorn/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 rios_app rios_app
    postrotate
        systemctl reload rios-desierto
    endscript
}

/var/log/nginx/rios_desierto_*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    sharedscripts
    postrotate
        systemctl reload nginx
    endscript
}
```

### 9.2 Script de Backup de Base de Datos
```bash
sudo nano /usr/local/bin/backup_rios_db.sh
```

Contenido:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/rios_desierto"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="rios_desierto_db"
DB_USER="rios_user"

mkdir -p $BACKUP_DIR

# Backup de PostgreSQL
pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Mantener solo los últimos 7 días de backups
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete

echo "Backup completado: $BACKUP_DIR/db_backup_$DATE.sql.gz"
```

```bash
sudo chmod +x /usr/local/bin/backup_rios_db.sh

# Programar backup diario
sudo crontab -e
# Agregar: 0 2 * * * /usr/local/bin/backup_rios_db.sh
```

---

## 🚀 PASO 10: Puesta en Marcha

### 10.1 Verificar Servicios
```bash
# Estado de todos los servicios
sudo systemctl status postgresql
sudo systemctl status nginx
sudo systemctl status rios-desierto

# Verificar puertos
sudo netstat -tlnp | grep -E ':80|:443|:8001|:5432'
```

### 10.2 Pruebas de Funcionalidad
```bash
# Probar API
curl -H "Accept: application/json" http://tu_dominio.com/api/clientes/buscar/?tipo_documento=CC&numero_documento=12345678

# Probar frontend
curl -I http://tu_dominio.com/

# Verificar logs
sudo tail -f /var/log/gunicorn/error.log
sudo tail -f /var/log/nginx/rios_desierto_error.log
```

---

## ⚡ PASO 11: Optimizaciones de Rendimiento

### 11.1 Configurar Caché en Nginx
Agregar al bloque `server` en nginx:
```nginx
# Cache para archivos estáticos
location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    access_log off;
}
```

### 11.2 Configurar Gzip en Nginx
```bash
sudo nano /etc/nginx/nginx.conf
```

Habilitar en el bloque `http`:
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_comp_level 6;
gzip_types
    text/plain
    text/css
    text/xml
    text/javascript
    application/json
    application/javascript
    application/xml+rss
    application/atom+xml;
```

---

## 📋 PASO 12: Checklist de Verificación Final

### ✅ Backend
- [ ] Django ejecutándose con Gunicorn
- [ ] Base de datos PostgreSQL conectada
- [ ] Migraciones aplicadas
- [ ] Archivos estáticos servidos correctamente
- [ ] API endpoints funcionando

### ✅ Frontend
- [ ] Build de React compilado
- [ ] Archivos servidos por Nginx
- [ ] API calls funcionando correctamente
- [ ] Exportación de archivos operativa

### ✅ Infraestructura
- [ ] Nginx configurado y funcionando
- [ ] SSL/HTTPS habilitado
- [ ] Firewall configurado
- [ ] Backups programados
- [ ] Logs configurados
- [ ] Monitoreo básico activo

### ✅ Seguridad
- [ ] DEBUG=False en producción
- [ ] SECRET_KEY segura
- [ ] ALLOWED_HOSTS configurados
- [ ] Headers de seguridad activos
- [ ] Permisos de archivos correctos

---

## 📞 URLs de Acceso en Producción

- **Aplicación principal:** https://tu_dominio.com
- **API Backend:** https://tu_dominio.com/api/
- **Panel de Admin Django:** https://tu_dominio.com/admin/
- **Búsqueda de clientes:** https://tu_dominio.com/api/clientes/buscar/
- **Reporte de fidelización:** https://tu_dominio.com/api/clientes/reporte-fidelizacion/

---

## 🔧 Comandos de Mantenimiento

### Reiniciar Servicios
```bash
sudo systemctl restart rios-desierto
sudo systemctl restart nginx
sudo systemctl restart postgresql
```

### Ver Logs en Tiempo Real
```bash
# Backend
sudo tail -f /var/log/gunicorn/error.log

# Nginx
sudo tail -f /var/log/nginx/rios_desierto_error.log

# Sistema
sudo journalctl -u rios-desierto -f
```

### Actualizar Aplicación
```bash
# Parar servicio
sudo systemctl stop rios-desierto

# Actualizar código
sudo -u rios_app git pull origin main

# Backend
cd /var/www/rios_desierto/backend/
sudo -u rios_app ./venv/bin/pip install -r requirements.txt
sudo -u rios_app ./venv/bin/python manage.py migrate
sudo -u rios_app ./venv/bin/python manage.py collectstatic --noinput

# Frontend
cd /var/www/rios_desierto/frontend/
sudo -u rios_app npm ci
sudo -u rios_app npm run build

# Reiniciar servicios
sudo systemctl start rios-desierto
sudo systemctl reload nginx
```

---

## 📈 Consideraciones de Escalabilidad

### Para Mayor Tráfico:
1. **Load Balancer:** Nginx como proxy reverso a múltiples instancias
2. **Base de datos:** PostgreSQL con réplicas de lectura
3. **Cache:** Redis para sesiones y cache de API
4. **CDN:** Para archivos estáticos y media
5. **Monitoreo:** Prometheus + Grafana
6. **Contenedores:** Docker + Kubernetes para escalabilidad automática

### Recursos Adicionales:
- **Monitoring:** New Relic, DataDog, o Sentry para errores
- **Backup:** Automatización con scripts personalizados o S3
- **CI/CD:** GitHub Actions, GitLab CI, o Jenkins
- **Documentación:** API docs con Django REST Framework browsable API

---

**🎉 ¡Implementación Completada!**

Tu sistema "Ríos del Desierto" está ahora ejecutándose en producción con todas las mejores prácticas de seguridad, rendimiento y mantenibilidad.

---

## 🐳 COMANDOS DOCKER ÚTILES

### Gestión de Contenedores
```bash
# Construir y ejecutar todos los servicios
docker-compose up --build -d

# Ver estado de contenedores
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend

# Ejecutar comandos en contenedores
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --noinput

# Parar servicios
docker-compose down

# Parar y eliminar volúmenes (⚠️ CUIDADO: Elimina datos)
docker-compose down -v
```

### Comandos de Desarrollo
```bash
# Desarrollo con hot-reload
docker-compose -f docker-compose.dev.yml up --build

# Ejecutar tests
docker-compose exec backend python manage.py test
docker-compose exec frontend npm test

# Acceder a la base de datos
docker-compose exec db psql -U rios_user -d rios_desierto_db

# Backup de base de datos
docker-compose exec db pg_dump -U rios_user rios_desierto_db > backup.sql

# Restaurar backup
cat backup.sql | docker-compose exec -T db psql -U rios_user -d rios_desierto_db
```

### Optimización de Imágenes
```bash
# Limpiar imágenes no utilizadas
docker system prune -a

# Ver tamaño de imágenes
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Construir imagen específica
docker build -t rios-backend:latest ./backend
docker build -t rios-frontend:latest ./frontend

# Ejecutar contenedor individual
docker run -p 8000:8000 rios-backend:latest
docker run -p 3000:80 rios-frontend:latest
```

---

## ☁️ COMANDOS GOOGLE CLOUD ÚTILES

### Gestión de Cloud Run
```bash
# Ver servicios desplegados
gcloud run services list --region=us-central1

# Ver logs del servicio
gcloud run logs tail --service=rios-backend --region=us-central1
gcloud run logs tail --service=rios-frontend --region=us-central1

# Ver URL de servicios
gcloud run services describe rios-backend --region=us-central1 --format="value(status.url)"
gcloud run services describe rios-frontend --region=us-central1 --format="value(status.url)"

# Configurar tráfico (Blue-Green deployment)
gcloud run services update-traffic rios-backend --to-revisions=LATEST=100 --region=us-central1

# Escalar servicio
gcloud run services update rios-backend --max-instances=20 --region=us-central1
```

### Gestión de Cloud SQL
```bash
# Conectar a la base de datos
gcloud sql connect rios-db-prod --user=rios_user

# Crear backup
gcloud sql backups create --instance=rios-db-prod --description="Manual backup $(date)"

# Listar backups
gcloud sql backups list --instance=rios-db-prod

# Restaurar backup
gcloud sql backups restore BACKUP_ID --restore-instance=rios-db-prod
```

### Gestión de Cloud Build
```bash
# Ver builds recientes
gcloud builds list --limit=10

# Ver logs de build específico
gcloud builds log BUILD_ID

# Ejecutar build manual
gcloud builds submit --config=cloudbuild.yaml

# Crear trigger desde CLI
gcloud builds triggers create github \
    --repo-name=rios-desierto \
    --repo-owner=TU_USUARIO \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml
```

---

## 📊 MONITOREO EN GOOGLE CLOUD

### Configurar Alertas
```bash
# Crear política de alerta para alta latencia
gcloud alpha monitoring policies create --policy-from-file=monitoring-policy.yaml

# Ver métricas del servicio
gcloud run services describe rios-backend \
    --region=us-central1 \
    --format="export" > service-config.yaml
```

### Dashboard de Monitoreo
- **Cloud Console:** https://console.cloud.google.com/run
- **Logging:** https://console.cloud.google.com/logs
- **Monitoring:** https://console.cloud.google.com/monitoring
- **Cloud SQL:** https://console.cloud.google.com/sql

---

## 🚀 URLs DE ACCESO EN PRODUCCIÓN (GOOGLE CLOUD)

```bash
# Obtener URLs dinámicamente
BACKEND_URL=$(gcloud run services describe rios-backend --region=us-central1 --format="value(status.url)")
FRONTEND_URL=$(gcloud run services describe rios-frontend --region=us-central1 --format="value(status.url)")

echo "🌐 URLs de Producción:"
echo "Frontend: $FRONTEND_URL"
echo "Backend API: $BACKEND_URL/api/"
echo "Admin Django: $BACKEND_URL/admin/"
echo "Búsqueda de clientes: $BACKEND_URL/api/clientes/buscar/"
echo "Reporte fidelización: $BACKEND_URL/api/clientes/reporte-fidelizacion/"
```

---

## 📈 CONSIDERACIONES DE COSTOS GCP

### Optimización de Costos
```bash
# Configurar mínimo de instancias en 0 (serverless)
gcloud run services update rios-backend --min-instances=0 --region=us-central1
gcloud run services update rios-frontend --min-instances=0 --region=us-central1

# Ver uso de recursos
gcloud run services describe rios-backend --region=us-central1 --format="yaml(spec.template.spec)"

# Configurar límites de CPU y memoria
gcloud run services update rios-backend \
    --memory=512Mi \
    --cpu=1 \
    --region=us-central1
```

### Estimación Mensual Actualizada
- **Cloud Run Backend:** $5-25 USD (con min-instances=0)
- **Cloud Run Frontend:** $5-15 USD (servido por CDN)
- **Cloud SQL f1-micro:** $7-15 USD
- **Cloud Storage:** $1-5 USD
- **Cloud Build:** $0-5 USD (builds automáticos)
- **Total Optimizado:** $18-65 USD/mes