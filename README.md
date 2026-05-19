# Supabase Bucket Example - API

## Motivacion

Este proyecto es un **ejemplo practico** de como integrar [Supabase Storage](https://supabase.com/docs/guides/storage) en una aplicacion Python para **subir imagenes a un bucket**.

El caso de uso es un formulario de registro de mascotas que incluye una foto. La imagen se sube al bucket de Supabase mediante su cliente oficial (`supabase-py`), mientras que el resto de los datos del formulario se persisten en la base de datos PostgreSQL de Supabase usando queries literales con SQLAlchemy `text()`.

El objetivo es servir de referencia para cualquier proyecto que necesite manejar subida de archivos a Supabase Storage desde un backend Python.

## Arquitectura

```
Flujo del POST /mascotas:

  Frontend (Web)
       |
       |  multipart/form-data (campos + imagen)
       v
  Flask API (este proyecto)
       |
       |--- Imagen ---> Supabase Storage (bucket)
       |
       |--- Datos  ---> Supabase PostgreSQL (queries literales)
       |
       v
  Respuesta JSON con la mascota creada
```

## Estructura del proyecto

```
supabase-bucket-example-api/
├── app.py                          # Entry point Flask (puerto 5000)
├── requirements.txt                # Dependencias Python
├── .env.example                    # Template para configurar DB + Supabase
├── bucket_example/
│   ├── constants.py                # Configuracion (DB + Supabase + validaciones)
│   ├── db.py                       # Capa de acceso a datos (queries literales)
│   ├── utils.py                    # Funciones de validacion reutilizables
│   ├── pagination.py               # Paginacion HATEOAS
│   ├── routes/
│   │   └── mascotas.py             # Endpoints REST
│   ├── services/
│   │   ├── mascotas.py             # Logica de negocio
│   │   └── storage.py              # Operaciones con Supabase Storage
│   └── validators/
│       └── mascotas.py             # Validacion de entrada
└── db/
    └── supabase_ddl.sql            # Esquema + datos iniciales (ejecutar en Supabase SQL Editor)
```

## Requisitos previos

- Python 3.10+
- Cuenta en [Supabase](https://supabase.com) con un proyecto creado

## Configuracion

### 1. Base de datos y Storage en Supabase

1. Crear un proyecto en [Supabase](https://supabase.com)
2. Ir al **SQL Editor** y ejecutar el script `db/supabase_ddl.sql` (crea la tabla, las policies RLS, el bucket de Storage y los datos de ejemplo)
3. Copiar `.env.example` a `.env` y completar las credenciales:

```bash
cp .env.example .env
```

```
DB_HOST=db.tu-proyecto.supabase.co
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=tu-db-password-aqui
DB_NAME=postgres

SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key-aqui
SUPABASE_BUCKET=mascotas-fotos
```

> Los datos de conexion a la base de datos se encuentran en **Settings > Database** del dashboard de Supabase.

### 2. Entorno virtual, instalacion y ejecucion

El proyecto incluye scripts de setup que crean el entorno virtual, instalan las dependencias y levantan la aplicacion automaticamente.

**Con virtualenv:**

```bash
# Windows
setup_virtualenv.bat

# Linux / macOS
chmod +x setup_virtualenv.sh
./setup_virtualenv.sh
```

**Con pipenv:**

```bash
# Windows
setup_pipenv.bat

# Linux / macOS
chmod +x setup_pipenv.sh
./setup_pipenv.sh
```

Una vez iniciada, la API estara disponible en `http://localhost:5000/bucket_example_api`

## Endpoints

| Metodo | Endpoint                        | Descripcion                              |
|--------|---------------------------------|------------------------------------------|
| GET    | `/mascotas`                     | Listar mascotas con filtros y paginacion |
| GET    | `/mascotas/disponibles`         | Mascotas disponibles para adopcion       |
| POST   | `/mascotas`                     | Crear mascota (multipart/form-data)      |
| GET    | `/mascotas/<id>`                | Obtener mascota por ID                   |
| PUT    | `/mascotas/<id>`                | Reemplazar mascota (JSON)                |
| PATCH  | `/mascotas/<id>`                | Actualizar parcialmente (JSON)           |
| DELETE | `/mascotas/<id>`                | Eliminar mascota                         |

### Ejemplo: Crear mascota con imagen

```bash
curl -X POST http://localhost:5000/bucket_example_api/mascotas \
  -F "nombre=Luna" \
  -F "especie=perro" \
  -F "raza=Labrador" \
  -F "edad_meses=24" \
  -F "sexo=hembra" \
  -F "descripcion=Perra muy carinosa" \
  -F "fecha_ingreso=2025-01-15" \
  -F "imagen=@/ruta/a/foto.jpg"
```

## Patron de queries literales

Este proyecto usa SQLAlchemy **sin ORM**, ejecutando SQL directamente con `text()`:

```python
from sqlalchemy import create_engine, text

motor = create_engine(DB_URL)

# SELECT
with motor.connect() as conexion:
    resultado = conexion.execute(text(sql), {'id': 1})

# INSERT/UPDATE/DELETE (con commit automatico)
with motor.begin() as conexion:
    resultado = conexion.execute(text(sql), parametros)
```

Ver `bucket_example/db.py` para todos los ejemplos de queries.
