from flask import Blueprint, jsonify, request
from ..constants import (
    ERROR_CODE_INVALID_BODY,
    ERROR_CODE_MASCOTA_NOT_FOUND,
    ERROR_CODE_IMAGE_UPLOAD_FAILED,
    ESPECIES_VALIDAS,
    SEXOS_VALIDOS,
    MAX_FILE_SIZE_MB
)
from ..utils import construir_error_api
from ..pagination import construir_respuesta_paginada
from ..validators.mascotas import validar_params_mascotas, validar_id_mascota
from ..services.mascotas import (
    filtrar_mascotas,
    listar_mascotas_disponibles,
    buscar_mascota_por_id,
    crear_mascota,
    reemplazar_mascota_service,
    actualizar_mascota_parcial,
    eliminar_mascota
)
from ..services.storage import subir_imagen

mascotas_bp = Blueprint('mascotas', __name__)


@mascotas_bp.route('/mascotas', methods=['GET'])
def get_mascotas():
    try:
        params = validar_params_mascotas(request.args.to_dict())
    except ValueError as e:
        return jsonify(e.args[0]), 400

    resultado = filtrar_mascotas(params)

    if not resultado:
        return '', 204

    paginado = resultado[params['offset']: params['offset'] + params['limit']]

    response = construir_respuesta_paginada(
        datos={'mascotas': paginado},
        total=len(resultado),
        offset=params['offset'],
        limit=params['limit'],
        base_url=request.base_url,
        params=request.args.to_dict()
    )

    return jsonify(response)


@mascotas_bp.route('/mascotas/disponibles', methods=['GET'])
def get_mascotas_disponibles():
    """Endpoint especifico para el frontend: retorna todas las mascotas disponibles para adopcion."""
    mascotas = listar_mascotas_disponibles()

    if not mascotas:
        return '', 204

    return jsonify({'mascotas': mascotas})


@mascotas_bp.route('/mascotas', methods=['POST'])
def post_mascota():
    """
    Crea una nueva mascota.
    Acepta multipart/form-data con los campos del formulario y un archivo 'imagen'.
    La imagen se sube al bucket de Supabase y los datos se guardan en MySQL.
    """
    # Validar que haya datos del formulario
    nombre        = request.form.get('nombre', '').strip()
    especie       = request.form.get('especie', '').strip()
    raza          = request.form.get('raza', '').strip()
    edad_meses    = request.form.get('edad_meses', '').strip()
    sexo          = request.form.get('sexo', '').strip()
    descripcion   = request.form.get('descripcion', '').strip()
    fecha_ingreso = request.form.get('fecha_ingreso', '').strip()
    archivo       = request.files.get('imagen')

    # Validaciones basicas de campos del formulario
    errores = []

    if not nombre:
        errores.append('El nombre es obligatorio.')
    if especie.lower() not in ESPECIES_VALIDAS:
        errores.append('La especie seleccionada no es valida.')
    if not raza:
        errores.append('La raza es obligatoria.')
    if not edad_meses:
        errores.append('La edad en meses es obligatoria.')
    else:
        try:
            edad_meses_int = int(edad_meses)
            if edad_meses_int < 0:
                errores.append('La edad en meses debe ser mayor o igual a 0.')
        except ValueError:
            errores.append('La edad en meses debe ser un numero entero.')
            edad_meses_int = None
    if sexo.lower() not in SEXOS_VALIDOS:
        errores.append('El sexo seleccionado no es valido.')
    if not descripcion:
        errores.append('La descripcion es obligatoria.')
    if not fecha_ingreso:
        errores.append('La fecha de ingreso es obligatoria.')
    if not archivo or not archivo.filename:
        errores.append('Debes enviar una imagen.')

    if errores:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Errores de validacion',
            description='; '.join(errores)
        )), 400

    # Subir imagen al bucket de Supabase
    img_foto = subir_imagen(archivo)
    
    if not img_foto:
        return jsonify(construir_error_api(
            code=ERROR_CODE_IMAGE_UPLOAD_FAILED,
            message='Error al subir la imagen',
            description=f'Verifica el formato de la imagen y que no supere los {MAX_FILE_SIZE_MB} MB.'
        )), 500

    # Insertar datos en MySQL via queries literales
    body = {
        'nombre':        nombre,
        'especie':       especie,
        'raza':          raza,
        'edad_meses':    edad_meses_int,
        'sexo':          sexo,
        'descripcion':   descripcion,
        'img_foto':      img_foto,
        'fecha_ingreso': fecha_ingreso
    }

    try:
        mascota = crear_mascota(body)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400

        return jsonify(e.args[0]), status

    return jsonify(mascota), 201


@mascotas_bp.route('/mascotas/<id>', methods=['GET'])
def get_mascota_por_id(id):
    try:
        id_mascota = validar_id_mascota(id)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    mascota = buscar_mascota_por_id(id_mascota)

    if not mascota:
        return jsonify(construir_error_api(
            code=ERROR_CODE_MASCOTA_NOT_FOUND,
            message='Mascota no encontrada',
            description=f"No existe una mascota con id '{id_mascota}'"
        )), 404

    return jsonify(mascota)


@mascotas_bp.route('/mascotas/<id>', methods=['PUT'])
def put_mascota(id):
    try:
        id_mascota = validar_id_mascota(id)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    body = request.get_json(silent=True)

    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud invalido',
            description='El cuerpo debe ser un JSON valido con Content-Type application/json'
        )), 400

    try:
        reemplazar_mascota_service(id_mascota, body)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400

        return jsonify(e.args[0]), status

    return '', 204


@mascotas_bp.route('/mascotas/<id>', methods=['PATCH'])
def patch_mascota(id):
    try:
        id_mascota = validar_id_mascota(id)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    body = request.get_json(silent=True)

    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud invalido',
            description='El cuerpo debe ser un JSON valido con Content-Type application/json'
        )), 400

    try:
        actualizar_mascota_parcial(id_mascota, body)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status

    return '', 204


@mascotas_bp.route('/mascotas/<id>', methods=['DELETE'])
def delete_mascota(id):
    try:
        id_mascota = validar_id_mascota(id)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    eliminada = eliminar_mascota(id_mascota)

    if not eliminada:
        return jsonify(construir_error_api(
            code=ERROR_CODE_MASCOTA_NOT_FOUND,
            message='Mascota no encontrada',
            description=f"No existe una mascota con id '{id_mascota}'"
        )), 404

    return '', 204
