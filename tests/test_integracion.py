"""Pruebas de integración: verifican Flask + PostgreSQL trabajando juntos."""
from db import get_connection


def crear(client, nombre, telefono="", email="", notas="", disponibilidad="Disponible"):
    return client.post(
        "/add",
        data={
            "nombre": nombre,
            "telefono": telefono,
            "email": email,
            "notas": notas,
            "disponibilidad": disponibilidad,
        },
    )


def editar(client, contacto_id, nombre, telefono="", email="", notas="", disponibilidad="Disponible"):
    return client.post(
        f"/edit/{contacto_id}",
        data={
            "nombre": nombre,
            "telefono": telefono,
            "email": email,
            "notas": notas,
            "disponibilidad": disponibilidad,
        },
    )


def contar_contactos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM contactos;")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total


# --- CRUD existente ---

def test_pagina_principal_responde(client):
    respuesta = client.get("/")
    assert respuesta.status_code == 200
    assert "Agenda de Contactos" in respuesta.get_data(as_text=True)


def test_crear_contacto_se_guarda_y_aparece_en_la_lista(client):
    respuesta = crear(client, "Ana Pérez", "3001234567", "ana@correo.com", "Amiga")
    assert respuesta.status_code == 302

    html = client.get("/").get_data(as_text=True)
    assert "Ana Pérez" in html
    assert "ana@correo.com" in html
    assert contar_contactos() == 1


def test_editar_contacto_actualiza_los_datos(client):
    crear(client, "Ana Pérez", "3001234567")

    respuesta = editar(client, 1, "Ana María Pérez", "3109876543", disponibilidad="No disponible")
    assert respuesta.status_code == 302

    html = client.get("/").get_data(as_text=True)
    assert "Ana María Pérez" in html
    assert "3109876543" in html


def test_editar_contacto_inexistente_devuelve_404(client):
    assert client.get("/edit/999").status_code == 404


def test_eliminar_contacto_lo_quita_de_la_base_de_datos(client):
    crear(client, "Ana Pérez")
    assert contar_contactos() == 1

    respuesta = client.post("/delete/1")
    assert respuesta.status_code == 302
    assert contar_contactos() == 0


# --- Funcionalidad nueva 1: búsqueda por nombre y filtro de disponibilidad ---

def test_buscar_por_nombre_muestra_solo_coincidencias(client):
    crear(client, "Ana Pérez")
    crear(client, "Carlos Gómez")

    contactos = client.get("/api/buscar?nombre=ana").get_json()
    assert [c["nombre"] for c in contactos] == ["Ana Pérez"]


def test_filtrar_por_disponibilidad(client):
    crear(client, "Ana Pérez", disponibilidad="Disponible")
    crear(client, "Carlos Gómez", disponibilidad="No disponible")

    contactos = client.get("/api/buscar?disponibilidad=No disponible").get_json()
    assert [c["nombre"] for c in contactos] == ["Carlos Gómez"]


def test_busqueda_sin_resultados_muestra_mensaje(client):
    crear(client, "Ana Pérez")
    html = client.get("/?nombre=zzz").get_data(as_text=True)
    assert "No se encontraron contactos" in html


# --- Funcionalidad nueva 2: validación de formato ---

def test_no_se_guarda_contacto_con_email_invalido(client):
    respuesta = crear(client, "Ana Pérez", email="correo-malo")
    assert respuesta.status_code == 400
    assert "El email no tiene un formato válido." in respuesta.get_data(as_text=True)
    assert contar_contactos() == 0


def test_no_se_guarda_contacto_sin_nombre(client):
    respuesta = crear(client, "", telefono="3001234567")
    assert respuesta.status_code == 400
    assert "El nombre es obligatorio." in respuesta.get_data(as_text=True)
    assert contar_contactos() == 0


def test_formulario_con_error_conserva_lo_escrito(client):
    respuesta = crear(client, "Ana Pérez", telefono="abc")
    html = respuesta.get_data(as_text=True)
    assert 'value="Ana Pérez"' in html
    assert 'value="abc"' in html


def test_editar_con_datos_invalidos_no_modifica_el_contacto(client):
    crear(client, "Ana Pérez", telefono="3001234567")

    respuesta = editar(client, 1, "Ana", telefono="abc")
    assert respuesta.status_code == 400
    assert "3001234567" in client.get("/").get_data(as_text=True)


# --- Funcionalidad nueva 2: control de duplicados ---

def test_no_se_guarda_contacto_con_telefono_duplicado(client):
    crear(client, "Ana Pérez", telefono="3001234567")

    respuesta = crear(client, "Otra Persona", telefono="300 123 4567")
    assert respuesta.status_code == 409
    assert "El teléfono ya está registrado para el contacto «Ana Pérez»." in respuesta.get_data(as_text=True)
    assert contar_contactos() == 1


def test_no_se_guarda_contacto_con_email_duplicado_sin_importar_mayusculas(client):
    crear(client, "Ana Pérez", email="ana@correo.com")

    respuesta = crear(client, "Otra Persona", email="ANA@Correo.com")
    assert respuesta.status_code == 409
    assert "El email ya está registrado" in respuesta.get_data(as_text=True)
    assert contar_contactos() == 1


def test_editar_un_contacto_sin_cambiar_su_telefono_no_es_duplicado(client):
    crear(client, "Ana Pérez", telefono="3001234567", email="ana@correo.com")

    respuesta = editar(client, 1, "Ana P.", telefono="3001234567", email="ana@correo.com")
    assert respuesta.status_code == 302


def test_editar_con_el_email_de_otro_contacto_es_duplicado(client):
    crear(client, "Ana Pérez", email="ana@correo.com")
    crear(client, "Carlos Gómez", email="carlos@correo.com")

    respuesta = editar(client, 2, "Carlos Gómez", email="ana@correo.com")
    assert respuesta.status_code == 409
    assert "carlos@correo.com" in client.get("/").get_data(as_text=True)


# --- Endpoint /api/validar-contacto ---

def test_api_validar_contacto_valido(client):
    respuesta = client.post("/api/validar-contacto", json={"nombre": "Ana", "email": "ana@correo.com"})
    assert respuesta.status_code == 200
    assert respuesta.get_json() == {"valido": True, "errores": []}


def test_api_validar_contacto_con_formato_invalido(client):
    respuesta = client.post("/api/validar-contacto", json={"nombre": "", "email": "malo"})
    cuerpo = respuesta.get_json()
    assert cuerpo["valido"] is False
    assert "El nombre es obligatorio." in cuerpo["errores"]
    assert "El email no tiene un formato válido." in cuerpo["errores"]


def test_api_validar_contacto_detecta_duplicado(client):
    crear(client, "Ana Pérez", telefono="3001234567")

    cuerpo = client.post("/api/validar-contacto", json={"nombre": "Otra", "telefono": "3001234567"}).get_json()
    assert cuerpo["valido"] is False
    assert "El teléfono ya está registrado para el contacto «Ana Pérez»." in cuerpo["errores"]


def test_api_validar_contacto_ignora_al_propio_contacto_al_editar(client):
    crear(client, "Ana Pérez", telefono="3001234567")

    cuerpo = client.post(
        "/api/validar-contacto", json={"id": 1, "nombre": "Ana", "telefono": "3001234567"}
    ).get_json()
    assert cuerpo["valido"] is True
