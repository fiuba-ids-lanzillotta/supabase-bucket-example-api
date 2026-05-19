import os
from dotenv import load_dotenv

load_dotenv()

FORMATO_FECHA = '%Y-%m-%d'

ESPECIES_VALIDAS = {'perro', 'gato', 'conejo', 'ave', 'otro'}
SEXOS_VALIDOS    = {'macho', 'hembra'}
ESTADOS_VALIDOS  = {'disponible', 'adoptado', 'en_proceso'}

MIN_OFFSET     = 0
MIN_LIMIT      = 1
MIN_ID         = 1
MIN_EDAD       = 0
DEFAULT_OFFSET = '0'
DEFAULT_LIMIT  = '10'

# URL base de la API
BASE_URL = '/bucket_example_api'

# Configuracion de la base de datos Supabase (PostgreSQL)
DB_HOST     = os.getenv('DB_HOST', '')
DB_PORT     = int(os.getenv('DB_PORT', '5432'))
DB_USER     = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME     = os.getenv('DB_NAME', 'postgres')
DB_URL      = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Configuracion de Supabase Storage (solo para el bucket de imagenes)
SUPABASE_URL    = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY    = os.getenv('SUPABASE_KEY', '')
SUPABASE_BUCKET = os.getenv('SUPABASE_BUCKET', 'mascotas-fotos')

# Extensiones de imagen permitidas
EXTENSIONES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE_MB = 5

# Codigos de error
ERROR_CODE_INVALID_BODY        = 'invalid.body'
ERROR_CODE_INVALID_MIN_VALUE   = 'invalid.min.value'
ERROR_CODE_MASCOTA_NOT_FOUND   = 'mascota.not.found'
ERROR_CODE_MASCOTA_EXISTS      = 'mascota.already.exists'
ERROR_CODE_IMAGE_UPLOAD_FAILED = 'image.upload.failed'
