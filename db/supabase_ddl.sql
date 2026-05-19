-- =============================================================
--  Supabase Bucket Example - Script DDL para Supabase (PostgreSQL)
-- =============================================================
--  Ejecutar este script en el SQL Editor de Supabase:
--  https://supabase.com/dashboard/project/<tu-proyecto>/sql
-- =============================================================

-- Tabla de mascotas
CREATE TABLE IF NOT EXISTS mascotas (
    id            BIGINT       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre        VARCHAR(100) NOT NULL,
    especie       VARCHAR(50)  NOT NULL,
    raza          VARCHAR(100) NOT NULL,
    edad_meses    INT          NOT NULL CHECK (edad_meses >= 0),
    sexo          VARCHAR(10)  NOT NULL CHECK (sexo IN ('macho', 'hembra')),
    descripcion   TEXT         NOT NULL,
    img_foto      VARCHAR(255) NOT NULL,
    estado        VARCHAR(20)  NOT NULL DEFAULT 'disponible'
                               CHECK (estado IN ('disponible', 'adoptado', 'en_proceso')),
    fecha_ingreso DATE         NOT NULL,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- Habilitar Row Level Security (recomendado en Supabase)
ALTER TABLE mascotas ENABLE ROW LEVEL SECURITY;

-- Politica: permitir lectura publica (SELECT)
CREATE POLICY "Lectura publica de mascotas"
    ON mascotas
    FOR SELECT
    TO anon
    USING (true);

-- Politica: permitir insercion publica (INSERT)
CREATE POLICY "Insercion publica de mascotas"
    ON mascotas
    FOR INSERT
    TO anon
    WITH CHECK (true);

-- Politica: permitir actualizacion publica (UPDATE)
CREATE POLICY "Actualizacion publica de mascotas"
    ON mascotas
    FOR UPDATE
    TO anon
    USING (true)
    WITH CHECK (true);

-- Politica: permitir eliminacion publica (DELETE)
CREATE POLICY "Eliminacion publica de mascotas"
    ON mascotas
    FOR DELETE
    TO anon
    USING (true);


-- =============================================================
--  Configuracion del bucket de Storage
-- =============================================================
--  1. Ir a Storage en el dashboard de Supabase
--  2. Crear un bucket llamado "mascotas-fotos"
--  3. Marcarlo como "Public" para que las imagenes sean accesibles
--  4. En Policies del bucket, agregar una politica de INSERT
--     para el rol "anon" con la condicion: true
--     (esto permite subir imagenes sin autenticacion)
--
--  Alternativamente, ejecutar:

INSERT INTO storage.buckets (id, name, public)
VALUES ('mascotas-fotos', 'mascotas-fotos', true)
ON CONFLICT (id) DO NOTHING;

-- Politica: permitir subida publica de archivos al bucket
CREATE POLICY "Subida publica de fotos"
    ON storage.objects
    FOR INSERT
    TO anon
    WITH CHECK (bucket_id = 'mascotas-fotos');

-- Politica: permitir lectura publica de archivos del bucket
CREATE POLICY "Lectura publica de fotos"
    ON storage.objects
    FOR SELECT
    TO anon
    USING (bucket_id = 'mascotas-fotos');


-- =============================================================
--  Datos de ejemplo (opcional)
-- =============================================================
INSERT INTO mascotas (nombre, especie, raza, edad_meses, sexo, descripcion, img_foto, estado, fecha_ingreso)
VALUES
    ('Luna',   'perro',  'Labrador Retriever', 24, 'hembra', 'Luna es una perra muy carinosa y juguetona. Le encanta correr y jugar con pelotas. Es ideal para familias con ninos.',                                    'placeholder.jpg', 'disponible', '2025-01-15'),
    ('Max',    'perro',  'Pastor Aleman',      36, 'macho',  'Max es un perro leal y protector. Tiene un excelente temperamento y esta entrenado en obediencia basica.',                                                 'placeholder.jpg', 'disponible', '2025-02-10'),
    ('Mia',    'gato',   'Siames',             12, 'hembra', 'Mia es una gatita elegante y tranquila. Le gusta dormir al sol y recibir caricias. Perfecta para departamentos.',                                         'placeholder.jpg', 'disponible', '2025-03-05'),
    ('Rocky',  'perro',  'Bulldog Frances',    18, 'macho',  'Rocky es un bulldog frances muy simpatico. Tiene mucha energia pero tambien disfruta de largas siestas en el sofa.',                                       'placeholder.jpg', 'disponible', '2025-03-20'),
    ('Nina',   'gato',   'Persa',               8, 'hembra', 'Nina es una gatita persa de pelaje hermoso. Es muy tranquila y le encanta que la cepillen. Necesita cuidados regulares de su pelo.',                      'placeholder.jpg', 'disponible', '2025-04-01'),
    ('Canela', 'conejo', 'Mini Lop',            6, 'hembra', 'Canela es una conejita adorable y docil. Es perfecta como primera mascota para ninos. Le gustan las zanahorias y el heno fresco.',                        'placeholder.jpg', 'disponible', '2025-05-01');
