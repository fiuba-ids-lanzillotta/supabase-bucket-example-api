import logging
from ..constants import ERROR_CODE_MASCOTA_NOT_FOUND
from ..utils import construir_error_api
from ..validators.mascotas import validar_body_mascota, validar_body_mascota_put, validar_body_mascota_patch
from .. import db
from .storage import obtener_imagen_base64

logger = logging.getLogger(__name__)


def construir_mascota_resumen_dto(mascota: dict) -> dict:
    """Construye el dict de respuesta basico de una mascota, para el listado."""
    return {
        'id':            mascota['id'],
        'nombre':        mascota['nombre'],
        'especie':       mascota['especie'],
        'raza':          mascota['raza'],
        'edad_meses':    mascota['edad_meses'],
        'sexo':          mascota['sexo'],
        'img_foto':      mascota['img_foto'],
        'img_base64':    obtener_imagen_base64(mascota['img_foto']),
        'estado':        mascota['estado']
    }


def construir_mascota_dto(mascota: dict) -> dict:
    """Construye el dict de respuesta completo de una mascota, incluyendo descripcion y fechas."""
    dto = construir_mascota_resumen_dto(mascota)
    dto['descripcion']   = mascota['descripcion']
    dto['fecha_ingreso'] = str(mascota['fecha_ingreso'])

    return dto


def filtrar_mascotas(params: dict) -> list[dict]:
    """Obtiene y filtra las mascotas segun los parametros de busqueda (especie, sexo, estado)."""
    mascotas = db.obtener_todas_las_mascotas(
        especie=params.get('especie'),
        sexo=params.get('sexo'),
        estado=params.get('estado')
    )

    return [construir_mascota_resumen_dto(m) for m in mascotas]


def listar_mascotas_disponibles() -> list[dict]:
    """Retorna las mascotas disponibles para adopcion con DTO completo."""
    mascotas = db.obtener_mascotas_disponibles()

    return [construir_mascota_dto(m) for m in mascotas]


def buscar_mascota_por_id(id_mascota: int) -> dict:
    """Busca una mascota por id y construye el DTO de respuesta. Retorna un dict vacio si no existe."""
    mascota_encontrada = db.obtener_mascota_por_id(id_mascota)

    if not mascota_encontrada:
        return {}

    return construir_mascota_dto(mascota_encontrada)


def crear_mascota(body: dict) -> dict:
    """Crea una nueva mascota aplicando validaciones de DTO."""
    datos = validar_body_mascota(body)

    nuevo_id = db.insertar_mascota(
        nombre=datos['nombre'],
        especie=datos['especie'],
        raza=datos['raza'],
        edad_meses=datos['edad_meses'],
        sexo=datos['sexo'],
        descripcion=datos['descripcion'],
        img_foto=datos['img_foto'],
        fecha_ingreso=datos['fecha_ingreso']
    )

    nueva_mascota = db.obtener_mascota_por_id(nuevo_id)

    return construir_mascota_dto(nueva_mascota)


def reemplazar_mascota_service(id_mascota: int, body: dict) -> None:
    """Reemplaza todos los campos de una mascota. Si no existe, lanza error."""
    mascota_existente = db.obtener_mascota_por_id(id_mascota)

    if not mascota_existente:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_MASCOTA_NOT_FOUND,
            message='Mascota no encontrada',
            description=f"No existe una mascota con id '{id_mascota}'"
        ), 404)

    datos = validar_body_mascota_put(body)

    db.reemplazar_mascota(
        id_mascota=id_mascota,
        nombre=datos['nombre'],
        especie=datos['especie'],
        raza=datos['raza'],
        edad_meses=datos['edad_meses'],
        sexo=datos['sexo'],
        descripcion=datos['descripcion'],
        img_foto=datos['img_foto'],
        estado=datos['estado'],
        fecha_ingreso=datos['fecha_ingreso']
    )


def actualizar_mascota_parcial(id_mascota: int, body: dict) -> None:
    """Actualiza solo los campos presentes en el body. La mascota debe existir."""
    mascota_existente = db.obtener_mascota_por_id(id_mascota)

    if not mascota_existente:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_MASCOTA_NOT_FOUND,
            message='Mascota no encontrada',
            description=f"No existe una mascota con id '{id_mascota}'"
        ), 404)

    datos = validar_body_mascota_patch(body)

    # Completar con los valores actuales los campos que no vienen en el body
    nombre        = datos.get('nombre',        mascota_existente['nombre'])
    especie       = datos.get('especie',       mascota_existente['especie'])
    raza          = datos.get('raza',          mascota_existente['raza'])
    edad_meses    = datos.get('edad_meses',    mascota_existente['edad_meses'])
    sexo          = datos.get('sexo',          mascota_existente['sexo'])
    descripcion   = datos.get('descripcion',   mascota_existente['descripcion'])
    img_foto      = datos.get('img_foto',      mascota_existente['img_foto'])
    estado        = datos.get('estado',        mascota_existente['estado'])
    fecha_ingreso = datos.get('fecha_ingreso', str(mascota_existente['fecha_ingreso']))

    db.reemplazar_mascota(id_mascota, nombre, especie, raza, edad_meses, sexo, descripcion, img_foto, estado, fecha_ingreso)


def eliminar_mascota(id_mascota: int) -> bool:
    """Elimina una mascota por id. Retorna True si fue eliminada, False si no existia."""
    return db.eliminar_mascota_por_id(id_mascota)
