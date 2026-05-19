from sqlalchemy import create_engine, text
from .constants import DB_URL

# Motor de conexion compartido por toda la aplicacion.
# El pool de conexiones lo maneja SQLAlchemy automaticamente.
motor = create_engine(DB_URL)


# ---------------------------------------------------------------
# Funciones de soporte
# ---------------------------------------------------------------

def fila_a_dict(fila) -> dict:
    """Convierte una fila del resultado de una query en un diccionario."""
    return dict(fila._mapping)


def ejecutar_consulta(sql: str, parametros: dict = None) -> list[dict]:
    """Ejecuta una SELECT y devuelve todas las filas como lista de dicts."""
    with motor.connect() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})

        return [fila_a_dict(fila) for fila in resultado]


def ejecutar_mutacion(sql: str, parametros: dict = None) -> int:
    """
    Ejecuta un INSERT, UPDATE o DELETE y hace commit.
    Si la query incluye RETURNING id, retorna el id generado; de lo contrario retorna 0.
    """
    with motor.begin() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})
        fila = resultado.fetchone() if resultado.returns_rows else None

        return fila[0] if fila else 0


# ---------------------------------------------------------------
# Queries de mascotas
# ---------------------------------------------------------------

SQL_BASE_MASCOTAS = """
    SELECT
        m.id,
        m.nombre,
        m.especie,
        m.raza,
        m.edad_meses,
        m.sexo,
        m.descripcion,
        m.img_foto,
        m.estado,
        m.fecha_ingreso
    FROM mascotas m
"""


def obtener_todas_las_mascotas(especie: str, sexo: str, estado: str) -> list[dict]:
    """
    Retorna las mascotas que coincidan con los filtros recibidos.
    Los parametros que sean None se ignoran (no se aplica ese filtro).
    """
    sql    = SQL_BASE_MASCOTAS
    where  = []
    params = {}

    if especie is not None:
        where.append('LOWER(m.especie) = LOWER(:especie)')
        params['especie'] = especie

    if sexo is not None:
        where.append('LOWER(m.sexo) = LOWER(:sexo)')
        params['sexo'] = sexo

    if estado is not None:
        where.append('LOWER(m.estado) = LOWER(:estado)')
        params['estado'] = estado

    if where:
        sql += ' WHERE ' + ' AND '.join(where)

    sql += ' ORDER BY m.id'

    return ejecutar_consulta(sql, params)


def obtener_mascotas_disponibles() -> list[dict]:
    """Retorna todas las mascotas con estado 'disponible', ordenadas por fecha de ingreso."""
    sql = SQL_BASE_MASCOTAS + " WHERE m.estado = 'disponible' ORDER BY m.fecha_ingreso DESC"

    return ejecutar_consulta(sql)


def obtener_mascota_por_id(id_mascota: int) -> dict:
    """Retorna la mascota con el id dado, o un dict vacio si no existe."""
    sql   = SQL_BASE_MASCOTAS + ' WHERE m.id = :id'
    filas = ejecutar_consulta(sql, {'id': id_mascota})

    return filas[0] if filas else {}


def insertar_mascota(nombre: str, especie: str, raza: str, edad_meses: int,
                     sexo: str, descripcion: str, img_foto: str, fecha_ingreso: str) -> int:
    """Inserta una nueva mascota y retorna el id generado."""
    sql = """
        INSERT INTO mascotas (nombre, especie, raza, edad_meses, sexo, descripcion, img_foto, estado, fecha_ingreso)
        VALUES (:nombre, :especie, :raza, :edad_meses, :sexo, :descripcion, :img_foto, 'disponible', :fecha_ingreso)
        RETURNING id
    """
    
    return ejecutar_mutacion(sql, {
        'nombre':        nombre,
        'especie':       especie,
        'raza':          raza,
        'edad_meses':    edad_meses,
        'sexo':          sexo,
        'descripcion':   descripcion,
        'img_foto':      img_foto,
        'fecha_ingreso': fecha_ingreso
    })


def reemplazar_mascota(id_mascota: int, nombre: str, especie: str, raza: str,
                       edad_meses: int, sexo: str, descripcion: str, img_foto: str,
                       estado: str, fecha_ingreso: str) -> None:
    """Reemplaza todos los campos de una mascota existente."""
    sql = """
        UPDATE mascotas
        SET nombre = :nombre, especie = :especie, raza = :raza, edad_meses = :edad_meses,
            sexo = :sexo, descripcion = :descripcion, img_foto = :img_foto,
            estado = :estado, fecha_ingreso = :fecha_ingreso
        WHERE id = :id
    """
    ejecutar_mutacion(sql, {
        'id':            id_mascota,
        'nombre':        nombre,
        'especie':       especie,
        'raza':          raza,
        'edad_meses':    edad_meses,
        'sexo':          sexo,
        'descripcion':   descripcion,
        'img_foto':      img_foto,
        'estado':        estado,
        'fecha_ingreso': fecha_ingreso
    })


def actualizar_estado_mascota(id_mascota: int, estado: str) -> None:
    """Actualiza unicamente el estado de una mascota."""
    sql = 'UPDATE mascotas SET estado = :estado WHERE id = :id'

    ejecutar_mutacion(sql, {'id': id_mascota, 'estado': estado})


def eliminar_mascota_por_id(id_mascota: int) -> bool:
    """Elimina una mascota por id. Retorna True si existia y fue eliminada, False si no existia."""
    filas = ejecutar_consulta('SELECT id FROM mascotas WHERE id = :id', {'id': id_mascota})

    if not filas:
        return False

    ejecutar_mutacion('DELETE FROM mascotas WHERE id = :id', {'id': id_mascota})

    return True
