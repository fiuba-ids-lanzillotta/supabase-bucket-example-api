import base64
import logging
import uuid

from supabase import create_client
from ..constants import SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET, EXTENSIONES_PERMITIDAS

logger = logging.getLogger(__name__)

# Cliente de Supabase (singleton)
_supabase = None


def _get_client():
    """Obtiene o crea el cliente de Supabase."""
    global _supabase

    if _supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            logger.error("SUPABASE_URL y SUPABASE_KEY deben estar configurados en el archivo .env")
            raise RuntimeError("Supabase no esta configurado. Revisa el archivo .env")
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
    return _supabase


# ---------------------------------------------------------------------------
#  Funciones publicas
# ---------------------------------------------------------------------------

def extension_valida(filename: str) -> bool:
    """Verifica que la extension del archivo sea permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSIONES_PERMITIDAS


def subir_imagen(archivo) -> str | None:
    """
    Sube una imagen al bucket de Supabase Storage.
    Retorna el path del archivo en el bucket, o None si falla.
    """
    if not archivo or not archivo.filename:
        return None

    if not extension_valida(archivo.filename):
        logger.error(f"Extension no permitida: {archivo.filename}")

        return None

    try:
        client = _get_client()
        extension = archivo.filename.rsplit('.', 1)[1].lower()
        # Generar nombre unico para evitar colisiones
        nombre_archivo = f"{uuid.uuid4().hex}.{extension}"

        contenido = archivo.read()
        content_type = archivo.content_type or 'image/jpeg'

        client.storage.from_(SUPABASE_BUCKET).upload(
            path=nombre_archivo,
            file=contenido,
            file_options={"content-type": content_type}
        )

        logger.info(f"Imagen subida exitosamente: {nombre_archivo}")
        return nombre_archivo

    except Exception as e:
        logger.error(f"Error al subir imagen a Supabase Storage: {e}")

        return None


def obtener_imagen_base64(img_foto: str) -> str:
    """
    Descarga una imagen del bucket de Supabase Storage y la retorna
    como un data URI en base64 (ej: 'data:image/jpeg;base64,...').
    """
    if not img_foto:
        return ''

    try:
        client = _get_client()
        contenido = client.storage.from_(SUPABASE_BUCKET).download(img_foto)

        extension = img_foto.rsplit('.', 1)[1].lower() if '.' in img_foto else 'jpeg'
        mime_type = f'image/{extension}'

        b64 = base64.b64encode(contenido).decode('utf-8')

        return f'data:{mime_type};base64,{b64}'
    except Exception as e:
        logger.error(f"Error al descargar imagen {img_foto} desde Supabase Storage: {e}")

        return ''
