from datetime import datetime
from re import sub
import logging
from .constants import (
    ESPECIES_VALIDAS,
    SEXOS_VALIDOS,
    ESTADOS_VALIDOS,
    ERROR_CODE_INVALID_MIN_VALUE,
    MIN_OFFSET,
    MIN_LIMIT,
    DEFAULT_OFFSET,
    DEFAULT_LIMIT
)

logger = logging.getLogger(__name__)


def construir_error_api(code: str, message: str, description: str, level: str = 'error') -> dict:
    return {
        'errors': [{
            'code': code,
            'message': message,
            'level': level,
            'description': description
        }]
    }


def validar_formato_fecha(fecha: str, formato: str, nombre: str = 'fecha') -> datetime:
    try:
        return datetime.strptime(fecha, formato)
    except ValueError:
        logger.warning(f"Formato de fecha invalido: '{fecha}' no cumple el formato '{formato}'")

        raise ValueError(construir_error_api(
            code=f'invalid.{nombre}.format',
            message=f"Formato de '{nombre}' invalido",
            description=f"El valor '{fecha}' no cumple el formato esperado '{formato}'"
        ))


def validar_entero(numero: str, nombre: str = 'numero') -> int:
    numero_sin_letras = sub('[a-zA-Z]+', '', numero)

    try:
        return int(numero_sin_letras)
    except ValueError:
        logger.warning(f"Valor numerico invalido: '{numero}' no puede convertirse a entero")

        raise ValueError(construir_error_api(
            code=f'invalid.{nombre}.format',
            message=f"Formato de '{nombre}' invalido",
            description=f"El valor '{numero}' no puede convertirse a un numero entero"
        ))


def validar_minimo(valor: int, minimo: int, nombre: str) -> int:
    if valor < minimo:
        logger.warning(f"Valor por debajo del minimo: '{nombre}' es {valor}, minimo esperado {minimo}")

        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_MIN_VALUE,
            message='Valor por debajo del minimo permitido',
            description=f"El parametro '{nombre}' debe ser mayor o igual a {minimo}. Se recibio: {valor}"
        ))

    return valor


def validar_enum(valor: str, valores_validos: set, nombre: str) -> str:
    if valor.lower() not in valores_validos:
        logger.warning(f"Valor invalido para '{nombre}': '{valor}'")

        raise ValueError(construir_error_api(
            code=f'invalid.{nombre}',
            message=f"'{nombre}' invalido",
            description=f"El valor '{valor}' no es valido. Valores aceptados: {', '.join(sorted(valores_validos))}"
        ))

    return valor.lower()


def validar_especie(especie: str) -> str:
    return validar_enum(especie, ESPECIES_VALIDAS, 'especie')


def validar_sexo(sexo: str) -> str:
    return validar_enum(sexo, SEXOS_VALIDOS, 'sexo')


def validar_estado(estado: str) -> str:
    return validar_enum(estado, ESTADOS_VALIDOS, 'estado')


def validar_params_paginacion(args: dict) -> dict:
    """Valida los query params _offset y _limit. Retorna un dict con los valores validados."""
    errores = []

    offset = MIN_OFFSET
    limit  = MIN_LIMIT

    try:
        offset = validar_minimo(validar_entero(args.get('_offset', DEFAULT_OFFSET), '_offset'), MIN_OFFSET, '_offset')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        limit = validar_minimo(validar_entero(args.get('_limit', DEFAULT_LIMIT), '_limit'), MIN_LIMIT, '_limit')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return {'offset': offset, 'limit': limit}
