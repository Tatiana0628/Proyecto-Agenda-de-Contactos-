import os
import time
import psycopg2

DB_HOST = os.environ.get("DB_HOST", "db")
DB_NAME = os.environ.get("DB_NAME", "agenda")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_PORT = os.environ.get("DB_PORT", "5432")


def get_connection():
    intentos = 10
    while intentos > 0:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                port=DB_PORT,
            )
            return conn
        except psycopg2.OperationalError:
            intentos -= 1
            time.sleep(3)
    raise Exception("No fue posible conectar a la base de datos")


def buscar_duplicados(telefono, email, excluir_id=None):
    """Devuelve mensajes de error si el teléfono o el email ya pertenecen a otro contacto.

    El teléfono se compara solo por dígitos y el email sin distinguir mayúsculas.
    excluir_id permite ignorar el propio contacto al editarlo.
    """
    from validaciones import normalizar_telefono, normalizar_email

    errores = []
    telefono = normalizar_telefono(telefono)
    email = normalizar_email(email)
    conn = get_connection()
    cur = conn.cursor()

    if telefono:
        cur.execute(
            "SELECT nombre FROM contactos WHERE regexp_replace(telefono, '\\D', '', 'g') = %s AND id <> %s LIMIT 1;",
            (telefono, excluir_id or 0),
        )
        fila = cur.fetchone()
        if fila:
            errores.append(f"El teléfono ya está registrado para el contacto «{fila[0]}».")

    if email:
        cur.execute(
            "SELECT nombre FROM contactos WHERE LOWER(TRIM(email)) = %s AND id <> %s LIMIT 1;",
            (email, excluir_id or 0),
        )
        fila = cur.fetchone()
        if fila:
            errores.append(f"El email ya está registrado para el contacto «{fila[0]}».")

    cur.close()
    conn.close()
    return errores


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS contactos (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            telefono VARCHAR(30),
            email VARCHAR(100),
            notas VARCHAR(255),
            disponibilidad VARCHAR(50) DEFAULT 'Disponible'
        );
        ALTER TABLE contactos ADD COLUMN IF NOT EXISTS disponibilidad VARCHAR(50) DEFAULT 'Disponible';
        UPDATE contactos SET disponibilidad = 'Disponible' WHERE disponibilidad IS NULL;
        """
    )
    conn.commit()
    cur.close()
    conn.close()