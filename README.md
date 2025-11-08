# 🏢 Sistema de Gestión de Clientes - Ríos del Desierto
## Prueba Técnica Falabella

[![Django](https://img.shields.io/badge/Django-5.0.6-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org/)

---

## 📋 Descripción del Proyecto

Sistema completo de gestión de clientes desarrollado con **Django REST Framework** y **React TypeScript** que permite:

✅ **Búsqueda de clientes** por múltiples criterios  
✅ **Consulta por número de documento**  
✅ **Exportación automatizada con Pandas** (CSV, Excel, TXT)  
✅ **Reporte de fidelización con análisis avanzado** para clientes con compras >$5MM COP/mes  
✅ **Procesamiento de datos optimizado con Pandas** para mejor performance  

---

## 🚀 Instalación Rápida con Docker

### Prerrequisitos
- [Docker](https://www.docker.com/get-started) y Docker Compose
- [Git](https://git-scm.com/)

### Instrucciones de Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/dhernandezgu02/prueba_rios_desierto.git
cd prueba_rios_desierto

# 2. Ejecutar con Docker
docker-compose up --build -d

# 3. Crear datos de prueba (opcional)
docker-compose exec backend python manage.py crear_datos_prueba

# Acceder al sistema
# Frontend: http://localhost:3000
# API: http://localhost:8000/api/
# Admin Django: http://localhost:8000/admin/
```

**¡Listo!** El sistema estará funcionando en pocos minutos.

---

## 🛠️ Instalación Manual (Alternativa)

### Prerrequisitos
- Python 3.11+
- Node.js 18+
- SQLite3 (incluido con Python)

### Backend (Django)
```bash
cd backend/
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configurar base de datos SQLite3
python manage.py migrate
python manage.py createsuperuser
python manage.py crear_datos_prueba

# Ejecutar servidor
python manage.py runserver 8000
```

### Frontend (React)
```bash
cd frontend/
npm install
npm start  # Desarrollo en puerto 3000
```

---

## 📊 Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Django | 5.0.6 | Backend API REST |
| Django REST Framework | 3.15+ | Serialización y API |
| **Pandas** | **2.0.3** | **Análisis y exportación de datos** |
| React | 18+ | Frontend SPA |
| TypeScript | 5+ | Tipado estático |
| SQLite3 | Integrado | Base de datos |
| Docker | Latest | Containerización |
| Nginx | Latest | Servidor web |

---

## 🎯 Funcionalidades Implementadas

### 1️⃣ Formulario de Búsqueda de Clientes
- Búsqueda por nombre, documento, email, teléfono
- Filtros avanzados por tipo de documento
- Resultados paginados y ordenables

### 2️⃣ Consulta por Número de Documento
- API endpoint: `GET /api/consulta-documento/{numero}/`
- Búsqueda exacta por número de documento
- Retorna información completa del cliente

### 3️⃣ Sistema de Exportación Automatizado con Pandas
- **CSV:** Formato estándar procesado con pandas
- **Excel:** Múltiples hojas con análisis automático
- **TXT:** Reporte estructurado con estadísticas
- Endpoints: `/api/clientes/exportar/{formato}/`
- **Análisis automático:** Estadísticas, tendencias y métricas

### 4️⃣ Reporte de Fidelización con Pandas
- Procesamiento automatizado de grandes volúmenes de datos
- Identifica clientes con compras >$5MM COP/mes
- Análisis estadístico avanzado con pandas
- Exportación multi-formato con métricas detalladas

---

## 📡 API Endpoints

### Clientes
```
GET    /api/clientes/buscar/           # Búsqueda de clientes
POST   /api/clientes/buscar/           # Búsqueda con filtros
GET    /api/consulta-documento/{num}/  # Consulta por documento
```

### Exportación Automatizada con Pandas
```
GET    /api/clientes/exportar/csv/     # CSV automatizado con pandas
GET    /api/clientes/exportar/excel/   # Excel multi-hoja con análisis  
GET    /api/clientes/exportar/txt/     # TXT estructurado con estadísticas
```

### Fidelización con Análisis Pandas
```
GET    /api/clientes/fidelizacion-report/  # Reporte avanzado con pandas
```

---

## 🗄️ Base de Datos

### Modelos Principales
- **TipoDocumento:** Tipos de identificación
- **Cliente:** Información de clientes
- **Compra:** Transacciones y estados

### Datos de Prueba
El comando `python manage.py crear_datos_prueba` crea:
- 20 clientes con diferentes tipos de documento
- 100+ compras con estados variados
- Clientes con compras >$5MM para testing de fidelización

---

## 🐳 Docker

### Servicios
- **frontend:** React app (puerto 3000)
- **backend:** Django API (puerto 8000)  
- **db:** PostgreSQL (puerto 5432)

### Comandos Útiles
```bash
# Ver logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Ejecutar comandos en contenedores
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser

# Backup de base de datos
docker-compose exec db pg_dump -U rios_user rios_desierto_db > backup.sql

# Reconstruir servicios
docker-compose up --build -d
```

---

## 🌐 Despliegue en Producción

Para despliegue en Google Cloud Platform, consultar: [**GUIA_IMPLEMENTACION_PRODUCCION.md**](./GUIA_IMPLEMENTACION_PRODUCCION.md)

---

## 🔧 Configuración de Desarrollo

### Variables de Entorno (.env)
```bash
DEBUG=True
SECRET_KEY=tu_secret_key
DB_NAME=rios_desierto_db
DB_USER=rios_user
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
```

### Estructura del Proyecto
```
prueba_rios_desierto/
├── backend/                 # Django API
│   ├── api/                # Modelos, vistas, serializers
│   ├── rios_desierto/      # Configuración Django
│   ├── requirements.txt    # Dependencias Python
│   └── Dockerfile
├── frontend/               # React App
│   ├── src/               # Componentes TypeScript
│   ├── package.json       # Dependencias Node
│   └── Dockerfile
├── docker-compose.yml     # Orquestación
├── cloudbuild.yaml       # CI/CD Google Cloud
└── README.md             # Esta documentación
```

---

## 👨‍💻 Desarrollado por

**Daniel Hernández**  
📧 dhernandezgu02@gmail.com  
🔗 [GitHub](https://github.com/dhernandezgu02)

---

## 📄 Licencia

Este proyecto fue desarrollado como prueba técnica para **Falabella**.

---

**🚀 ¡Gracias por revisar este proyecto!**