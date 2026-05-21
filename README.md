# Supabase Bucket Example - API

> **Aviso:** este proyecto es **codigo de ejemplo** con fines didacticos. Puede contener errores, simplificaciones o decisiones de diseno discutibles. Si se usa como base para un trabajo practico u otro entregable, **debe adaptarse a las buenas practicas y consignas especificas de la materia/catedra** (estilo de codigo, manejo de errores, validaciones, tests, seguridad, persistencia, etc.).

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

## Glosario de terminos

- **API REST**: estilo de arquitectura para servicios web que expone recursos via HTTP (GET, POST, PUT, DELETE) usando, en general, JSON como formato de intercambio.
- **Endpoint**: ruta concreta de la API (por ejemplo `POST /mascotas`) que responde a un metodo HTTP y realiza una accion sobre un recurso.
- **Request / Response**: par de mensajes HTTP. La **request** es lo que envia el cliente (metodo, headers, body); la **response** es lo que devuelve el servidor (status code, headers, body).
- **Status code**: codigo numerico de la respuesta HTTP. Por ejemplo: `200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `404 Not Found`.
- **Body**: contenido (payload) de una request o response. Las creaciones de mascota llegan como `multipart/form-data`; el resto de respuestas son JSON.
- **JSON**: formato de texto para representar datos estructurados (objetos y arrays).
- **`multipart/form-data`**: codificacion HTTP estandar para enviar formularios que contienen archivos. Se usa para recibir la foto de la mascota desde el frontend.
- **Flask**: micro framework web de Python. En este ejemplo se usa tanto en el frontend (renderizado server-side) como en la API backend.
- **Frontend**: aplicacion que renderiza las paginas HTML del lado del servidor y consume la API. En este ejemplo integrador corre en el puerto 5001 (`supabase-bucket-example-web`).
- **Backend / API**: servicio HTTP REST (este proyecto) que expone los endpoints de mascotas y se encarga de subir las imagenes a Supabase. Corre en el puerto 5000.
- **Blueprint (Flask)**: mecanismo de Flask para agrupar rutas relacionadas en modulos (por ejemplo `routes/mascotas.py`).
- **Validator**: funcion que verifica que el body / form de la request cumple las reglas (campos requeridos, formato, tipo de archivo). Viven en `validators/`.
- **Service**: capa con la **logica de negocio** (crear mascota, subir imagen al bucket). Vive en `services/` y es invocada desde las routes.
- **DTO (Data Transfer Object)**: estructura usada para pasar datos entre capas. En este proyecto se modelan como `dict` de Python (estilo funcional, sin clases).
- **CORS (Cross-Origin Resource Sharing)**: mecanismo del navegador que controla que dominios pueden consumir la API. Relevante cuando el frontend corre en otro origen.
- **Supabase**: plataforma backend-as-a-service que combina PostgreSQL, autenticacion, Storage (buckets) y otros servicios. En este ejemplo se usa PostgreSQL + Storage.
- **PostgreSQL**: motor de base de datos relacional gestionado por Supabase. Aca se accede via SQLAlchemy + queries literales.
- **Supabase Storage**: servicio de almacenamiento de archivos de Supabase, organizado en buckets.
- **Bucket**: contenedor de archivos publico o privado en Supabase Storage. La API sube las imagenes ahi y guarda la URL publica en la base.
- **Policy / RLS (Row Level Security)**: reglas de PostgreSQL/Supabase que controlan que filas y operaciones puede ejecutar cada usuario. Se definen en `db/supabase_ddl.sql`.
- **`supabase-py`**: cliente oficial de Supabase para Python. Se usa para subir archivos al bucket y obtener su URL publica.
- **`SUPABASE_URL` / `SUPABASE_KEY`**: credenciales para conectarse al proyecto de Supabase. Se cargan desde `.env`.
- **SQLAlchemy**: libreria de Python para hablar con bases SQL. Aca se usa **sin ORM**, ejecutando SQL literal con `text()`.
- **ORM (Object Relational Mapper)**: capa que mapea tablas a clases/objetos. Este proyecto **no** lo usa para mantener el SQL explicito.
- **Query parametrizada**: query SQL en la que los valores se pasan como parametros (`:id`) y no concatenados al string, evitando **SQL injection**.
- **SQL injection**: vulnerabilidad por la que un atacante inyecta SQL malicioso a traves de inputs no sanitizados.
- **Migracion / esquema**: definicion de la estructura de la base (tablas, columnas, policies). Aca vive en `db/supabase_ddl.sql`.
- **`.env` / variables de entorno**: archivo con configuracion sensible (credenciales, secretos) que **no** se commitea al repo. `.env.example` es la plantilla.
- **Entorno virtual**: directorio aislado con la version de Python y las dependencias del proyecto, para no mezclarlas con las del sistema.
- **virtualenv / `venv`**: herramienta estandar de Python para crear entornos virtuales. Las dependencias se declaran en `requirements.txt` y se instalan con `pip install -r requirements.txt`. En este proyecto lo levantan los scripts `setup_virtualenv.sh` / `setup_virtualenv.bat`.
- **pipenv**: herramienta alternativa que combina la gestion del entorno virtual con la de dependencias en un solo flujo. Usa `Pipfile` (declaracion) y `Pipfile.lock` (versiones exactas resueltas) en vez de `requirements.txt`. En este proyecto lo levantan los scripts `setup_pipenv.sh` / `setup_pipenv.bat`.
- **`pip`**: gestor de paquetes de Python. Instala librerias desde PyPI dentro del entorno activo.
