
import os

# Configurar la conexión antes de importar la aplicación.
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "agenda_test"
os.environ["DB_USER"] = "postgres"
os.environ["DB_PASSWORD"] = "postgres"

import pytest

from app import app
from db import get_connection


@pytest.fixture(scope="session", autouse=True)
def preparar_base_de_datos():
    """Comprueba que la base de pruebas existe y prepara sus tablas."""
    if os.environ["DB_NAME"] != "agenda_test":
        raise RuntimeError("Las pruebas deben usar agenda_test")

    conn = get_connection()
    conn.close()


@pytest.fixture(autouse=True)
def limpiar_base_de_datos():
    """Deja la tabla de contactos vacía antes de cada prueba."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("TRUNCATE TABLE contactos RESTART IDENTITY CASCADE;")

    conn.commit()
    cur.close()
    conn.close()


@pytest.fixture
def client():
    """Proporciona un cliente para probar las rutas de Flask."""
    app.config["TESTING"] = True

    with app.test_client() as cliente:
        yield cliente
