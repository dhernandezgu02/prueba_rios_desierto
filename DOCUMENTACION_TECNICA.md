# 📚 Documentación Técnica - Sistema Ríos del Desierto

## Información General

**Proyecto:** Sistema de Gestión de Clientes  
**Cliente:** Falabella (Prueba Técnica)  
**Desarrollador:** Daniel Hernández  
**Tecnología Principal:** Django + React + Pandas  

---

## 🎯 Objetivo del Sistema

Sistema web que permite gestionar clientes y sus compras, con funciones de búsqueda, consulta por documento, exportación de datos y reportes de fidelización automatizados.

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Base de       │
│   React/TS      │◄──►│  Django REST    │◄──►│   Datos         │
│   Puerto 3000   │    │   Puerto 8000   │    │   SQLite3       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Componentes Principales

- **Frontend:** React con TypeScript para la interfaz de usuario
- **Backend:** Django con REST Framework para la API
- **Base de Datos:** SQLite3 para almacenar información
- **Análisis:** Pandas para procesamiento y exportación de datos

---

## 📂 Estructura del Proyecto

```
proyecto/
├── backend/                    # API Django
│   ├── rios_desierto/         # Configuración principal
│   ├── clientes/              # App principal
│   │   ├── models.py          # Modelos de datos
│   │   ├── views.py           # Lógica de API
│   │   ├── serializers.py     # Serialización JSON
│   │   └── urls.py           # Rutas API
│   └── manage.py             # Comando Django
├── frontend/                  # App React
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   └── services/         # Llamadas API
│   └── package.json
└── docker-compose.yml        # Contenedores
```

---

## 🗄️ Modelos de Datos

### TipoDocumento
```python
- id: Identificador único
- nombre: Nombre del tipo (ej: "Cédula", "Pasaporte")
- activo: Si está disponible para uso
```

### Cliente
```python
- id: Identificador único
- tipo_documento: Relación con TipoDocumento
- numero_documento: Número de identificación
- nombre: Nombre del cliente
- apellido: Apellido del cliente
- email: Correo electrónico
- telefono: Número telefónico
- direccion: Dirección completa
- ciudad: Ciudad de residencia
- departamento: Departamento/Estado
- fecha_registro: Cuándo se registró
- activo: Si el cliente está activo
```

### Compra
```python
- id: Identificador único
- cliente: Relación con Cliente
- fecha_compra: Fecha de la transacción
- monto: Valor de la compra
- estado: Estado actual (PENDIENTE, COMPLETADA, etc.)
- descripcion: Detalles de la compra
```

---

## 🔌 API Endpoints

### Búsqueda y Consulta
```
GET /api/clientes/buscar/?query=texto
    Busca clientes por nombre, email, teléfono, documento

GET /api/clientes/consulta/12345678/
    Consulta cliente específico por número de documento
```

### Exportación (con Pandas)
```
GET /api/clientes/exportar/csv/
    Exporta todos los clientes en formato CSV

GET /api/clientes/exportar/excel/
    Exporta con múltiples hojas y análisis automático

GET /api/clientes/exportar/txt/
    Reporte estructurado en texto plano
```

### Reportes de Fidelización
```
GET /api/clientes/reporte/fidelizacion/
    Clientes con compras >$5,000,000 COP mensuales
```

---

## 🛠️ Funciones Principales

### 1. Búsqueda de Clientes
- **Archivo:** `frontend/src/components/SearchForm.tsx`
- **Función:** Permite buscar por múltiples criterios
- **API:** `GET /api/clientes/buscar/`

### 2. Consulta por Documento
- **Archivo:** `backend/clientes/views.py` → `consultar_cliente_por_documento`
- **Función:** Búsqueda exacta por número de documento
- **API:** `GET /api/clientes/consulta/{numero}/`

### 3. Exportación Automatizada
- **Archivo:** `backend/clientes/views.py` → `exportar_*_pandas`
- **Función:** Genera archivos usando pandas para análisis automático
- **Formatos:** CSV, Excel (multi-hoja), TXT

### 4. Reporte de Fidelización
- **Archivo:** `backend/clientes/views.py` → `reporte_fidelizacion_excel`
- **Función:** Identifica clientes de alto valor mensual
- **Criterio:** >$5,000,000 COP en compras por mes

---

## 🐍 Uso de Pandas

### Ventajas Implementadas
- **Performance:** Procesamiento rápido de grandes datasets
- **Análisis Automático:** Estadísticas y métricas calculadas automáticamente
- **Exportación Avanzada:** Múltiples formatos con formateo profesional
- **Flexibilidad:** Fácil modificación de criterios y filtros

### Ejemplos de Uso
```python
# Procesamiento de datos
df_clientes = pd.DataFrame(list(clientes_data))
df_compras = pd.DataFrame(list(compras_data))

# Análisis automático
analisis = df_compras.groupby('estado').agg({
    'monto': ['sum', 'mean', 'count']
})

# Exportación
df_export.to_excel(writer, sheet_name='Clientes', index=False)
```

---

## ⚙️ Configuración de Desarrollo

### Variables de Entorno
```bash
DEBUG=True
SECRET_KEY=tu_clave_secreta
# SQLite3 se configura automáticamente
# No requiere configuración adicional de base de datos
```

### Comandos Principales
```bash
# Backend
python manage.py runserver 8000
python manage.py migrate
python manage.py crear_datos_prueba

# Frontend
npm start
npm run build

# Docker
docker-compose up --build
```

---

## 🧪 Datos de Prueba

El sistema incluye un comando que crea datos de ejemplo:

```bash
python manage.py crear_datos_prueba
```

**Genera:**
- 20 clientes con diferentes tipos de documento
- 100+ compras con estados variados
- Clientes con compras >$5MM para testing de fidelización
- Datos realistas para Colombia

---

## 🔍 Funcionalidades por Pantalla

### Pantalla Principal
- Formulario de búsqueda de clientes
- Filtros por tipo de documento
- Resultados paginados

### Resultados de Búsqueda
- Lista de clientes encontrados
- Botones de exportación (CSV, Excel, TXT)
- Acceso a detalles del cliente

### Reporte de Fidelización
- Lista de clientes de alto valor
- Estadísticas automáticas
- Exportación en Excel con múltiples hojas

---

## 🚀 Despliegue

### Local con Docker
```bash
git clone https://github.com/dhernandezgu02/prueba_rios_desierto.git
cd prueba_rios_desierto
docker-compose up --build
```

### URLs de Acceso
- **Frontend:** http://localhost:3000
- **API:** http://localhost:8000/api/
- **Admin Django:** http://localhost:8000/admin/

---

## 📋 Checklist Técnico

### ✅ Completado
- [x] Modelos de datos con relaciones
- [x] API REST funcional
- [x] Frontend React con TypeScript
- [x] Búsqueda de clientes
- [x] Consulta por documento
- [x] Exportación con pandas (CSV, Excel, TXT)
- [x] Reporte de fidelización automatizado
- [x] Contenedores Docker
- [x] Datos de prueba
- [x] Documentación

### 🔧 Tecnologías Utilizadas
- **Backend:** Django 5.0.6, Django REST Framework
- **Frontend:** React 18, TypeScript
- **Análisis:** Pandas, Numpy
- **Base de Datos:** SQLite3 (integrado con Django)
- **Contenedores:** Docker, Docker Compose

---

## 📞 Soporte

**Desarrollador:** Daniel Hernández  
**Email:** dhernandezgu02@gmail.com  
**GitHub:** https://github.com/dhernandezgu02/prueba_rios_desierto  

---

**Documentación generada para Prueba Técnica Falabella**  
**Fecha:** Noviembre 2025