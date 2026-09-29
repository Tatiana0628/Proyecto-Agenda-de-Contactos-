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
            notas VARCHAR(255)
        );
        """
    )
    conn.commit()
    cur.close()
    conn.close()