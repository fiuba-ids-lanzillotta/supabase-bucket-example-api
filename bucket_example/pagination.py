from urllib.parse import urlencode

# Nombre de cada relacion en los links HATEOAS
NOMBRE_LINKS = {
    "PRIMERO":   "_first",
    "ANTERIOR":  "_prev",
    "SIGUIENTE": "_next",
    "ULTIMO":    "_last"
}

# Parametros de paginacion que se eliminan de la query string al armar links,
# para evitar que aparezcan duplicados en las URLs navegables.
PARAMS_PAGINACION = {"_offset", "_limit"}


def construir_link(tipo_link, offset, limit, base_url, params):
    """
    Construye un link de paginacion (HATEOAS) con el offset y limit indicados.

    Parametros:
        tipo_link (str): Tipo de link ('PRIMERO', 'ANTERIOR', 'SIGUIENTE', 'ULTIMO')
        offset (int):    Posicion de inicio para el link generado
        limit (int):     Cantidad de elementos por pagina
        base_url (str):  URL base del endpoint (sin query params)
        params (dict):   Query params actuales del request

    Retorna:
        tuple: (nombre_del_link, dict_con_href)
    """

    # Quitar los params de paginacion existentes para no duplicarlos
    params_filtrados = {
        k: v for k, v in params.items()
        if k not in PARAMS_PAGINACION
    }

    # Agregar los nuevos valores de paginacion
    params_filtrados["_offset"] = offset
    params_filtrados["_limit"]  = limit

    query_string = urlencode(params_filtrados)

    return NOMBRE_LINKS[tipo_link], {
        "href": f"{base_url}?{query_string}"
    }


def construir_links_paginacion(offset, limit, total, base_url, params):
    """
    Genera los links de paginacion disponibles segun la posicion actual en la coleccion.

    Parametros:
        offset (int):    Posicion actual (desde donde empieza la pagina)
        limit (int):     Cantidad de elementos por pagina
        total (int):     Total de elementos en la coleccion
        base_url (str):  URL base del endpoint
        params (dict):   Query params actuales del request

    Retorna:
        dict con los links HATEOAS disponibles (first, prev, next, last)
    """

    links = {}

    # Siempre se incluye el link al inicio
    rel, link = construir_link("PRIMERO", 0, limit, base_url, params)
    links[rel] = link

    # Link al bloque anterior (solo si no estamos al principio)
    if offset > 0:
        offset_anterior = max(offset - limit, 0)
        rel, link = construir_link("ANTERIOR", offset_anterior, limit, base_url, params)
        links[rel] = link

    # Link al bloque siguiente (solo si hay mas elementos)
    offset_siguiente = offset + limit
    
    if offset_siguiente < total:
        rel, link = construir_link("SIGUIENTE", offset_siguiente, limit, base_url, params)
        links[rel] = link

    # Link al ultimo bloque (solo si no estamos ya en el)
    offset_ultimo = 0 if total == 0 else ((total - 1) // limit) * limit

    if offset < offset_ultimo:
        rel, link = construir_link("ULTIMO", offset_ultimo, limit, base_url, params)
        links[rel] = link

    return links


def construir_respuesta_paginada(datos, total, offset, limit, base_url, params):
    """
    Construye el dict de respuesta paginada con los datos y los links HATEOAS.

    Parametros:
        datos (dict):   Un dict con una sola key cuyo valor es la lista de resultados.
                        Ejemplo: {'mascotas': [...]}
        total (int):    Total de elementos en la coleccion (sin paginar)
        offset (int):   Posicion actual
        limit (int):    Cantidad de elementos por pagina
        base_url (str): URL base del endpoint
        params (dict):  Query params actuales del request

    Retorna:
        dict con la lista de resultados y los links de navegacion
    """

    if not isinstance(datos, dict) or len(datos) != 1:
        raise ValueError("'datos' debe ser un dict con exactamente una sola key")

    nombre_coleccion, lista_datos = next(iter(datos.items()))

    return {
        nombre_coleccion: lista_datos,
        "_links": construir_links_paginacion(
            offset, limit, total, base_url, params
        )
    }
