from ..constants import (
    FORMATO_FECHA,
    MIN_OFFSET,
    MIN_LIMIT,
    MIN_EDAD,
    MIN_ID
)
from ..utils import (
    construir_error_api, validar_formato_fecha, validar_entero,
    validar_minimo, validar_especie, validar_sexo, validar_estado,
    validar_params_paginacion
)


def validar_params_mascotas(args: dict) -> dict:
    """Valida los query params del listado de mascotas.

    Acumula todos los errores de formato antes de lanzar,
    para que el cliente reciba el conjunto completo de problemas.
    """
    errores = []

    # Validar paginacion con la funcion compartida
    paginacion = {}
    try:
        paginacion = validar_params_paginacion(args)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    especie = args.get('especie')

    if especie is not None:
        try:
            especie = validar_especie(especie)
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    sexo = args.get('sexo')

    if sexo is not None:
        try:
            sexo = validar_sexo(sexo)
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    estado = args.get('estado')

    if estado is not None:
        try:
            estado = validar_estado(estado)
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return {
        'especie': especie,
        'sexo':    sexo,
        'estado':  estado,
        'offset':  paginacion.get('offset', MIN_OFFSET),
        'limit':   paginacion.get('limit',  MIN_LIMIT)
    }


def validar_body_mascota(body: dict) -> dict:
    """Valida que el cuerpo del POST /mascotas tenga los campos requeridos y con el formato correcto."""
    errores = []
    campos_requeridos = ['nombre', 'especie', 'raza', 'edad_meses', 'sexo', 'descripcion', 'img_foto', 'fecha_ingreso']

    for campo in campos_requeridos:
        if campo not in body or (isinstance(body.get(campo), str) and not body[campo]):
            errores.append(construir_error_api(
                code=f'required.{campo}',
                message=f"Campo requerido: '{campo}'",
                description=f"El campo '{campo}' es obligatorio y no puede estar vacio"
            )['errors'][0])

    if errores:
        raise ValueError({'errors': errores})

    especie_validada = None
    sexo_validado    = None

    try:
        especie_validada = validar_especie(body['especie'])
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        sexo_validado = validar_sexo(body['sexo'])
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        validar_formato_fecha(body['fecha_ingreso'], FORMATO_FECHA, 'fecha_ingreso')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    edad = 0
    
    try:
        edad = validar_entero(str(body['edad_meses']), 'edad_meses')
        edad = validar_minimo(edad, MIN_EDAD, 'edad_meses')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return {
        'nombre':        body['nombre'],
        'especie':       especie_validada,
        'raza':          body['raza'],
        'edad_meses':    edad,
        'sexo':          sexo_validado,
        'descripcion':   body['descripcion'],
        'img_foto':      body['img_foto'],
        'fecha_ingreso': body['fecha_ingreso']
    }


def validar_body_mascota_put(body: dict) -> dict:
    """Valida el body del PUT /mascotas/{id}: todos los campos son obligatorios mas el estado."""
    datos = validar_body_mascota(body)

    if 'estado' not in body or not body['estado']:
        raise ValueError(construir_error_api(
            code='required.estado',
            message="Campo requerido: 'estado'",
            description="El campo 'estado' es obligatorio para actualizar una mascota"
        ))

    try:
        datos['estado'] = validar_estado(body['estado'])
    except ValueError as e:
        raise

    return datos


def validar_body_mascota_patch(body: dict) -> dict:
    """Valida el body del PATCH /mascotas/{id}: al menos un campo valido y no vacio debe estar presente."""
    campos_conocidos = {'nombre', 'especie', 'raza', 'edad_meses', 'sexo', 'descripcion', 'img_foto', 'estado', 'fecha_ingreso'}
    campos_presentes = {k for k in body if k in campos_conocidos and body[k] is not None and body[k] != ''}

    if not campos_presentes:
        raise ValueError(construir_error_api(
            code='invalid.body',
            message='Cuerpo de la solicitud invalido',
            description='El cuerpo debe contener al menos un campo valido y no vacio'
        ))

    errores = []
    datos = {}

    if 'especie' in campos_presentes:
        try:
            datos['especie'] = validar_especie(body['especie'])
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if 'sexo' in campos_presentes:
        try:
            datos['sexo'] = validar_sexo(body['sexo'])
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if 'estado' in campos_presentes:
        try:
            datos['estado'] = validar_estado(body['estado'])
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if 'fecha_ingreso' in campos_presentes:
        try:
            validar_formato_fecha(body['fecha_ingreso'], FORMATO_FECHA, 'fecha_ingreso')
            datos['fecha_ingreso'] = body['fecha_ingreso']
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if 'edad_meses' in campos_presentes:
        try:
            datos['edad_meses'] = validar_minimo(validar_entero(str(body['edad_meses']), 'edad_meses'), MIN_EDAD, 'edad_meses')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    for campo in ('nombre', 'raza', 'descripcion', 'img_foto'):
        if campo in campos_presentes:
            datos[campo] = body[campo]

    return datos


def validar_id_mascota(id_str: str) -> int:
    """Valida que el id recibido en la URL sea un entero valido y mayor a cero."""
    id_mascota = validar_entero(id_str, 'id')

    return validar_minimo(id_mascota, MIN_ID, 'id')
