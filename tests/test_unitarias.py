"""Pruebas unitarias: verifican la función de validación de forma aislada (sin base de datos)."""
from validaciones import validar_contacto, normalizar_telefono, normalizar_email


def test_contacto_con_datos_validos_no_tiene_errores():
    errores = validar_contacto("Ana Pérez", "3001234567", "ana@correo.com", "Amiga")
    assert errores == []


def test_solo_el_nombre_es_obligatorio():
    assert validar_contacto("Ana", "", "", "") == []


def test_nombre_vacio_es_invalido():
    errores = validar_contacto("", "3001234567", "ana@correo.com", "")
    assert "El nombre es obligatorio." in errores


def test_nombre_con_solo_espacios_es_invalido():
    errores = validar_contacto("    ", "", "", "")
    assert "El nombre es obligatorio." in errores


def test_nombre_demasiado_largo_es_invalido():
    errores = validar_contacto("a" * 101, "", "", "")
    assert "El nombre no puede superar 100 caracteres." in errores


def test_email_sin_arroba_es_invalido():
    errores = validar_contacto("Ana", "", "anacorreo.com", "")
    assert "El email no tiene un formato válido." in errores


def test_email_sin_dominio_es_invalido():
    errores = validar_contacto("Ana", "", "ana@correo", "")
    assert "El email no tiene un formato válido." in errores


def test_telefono_con_letras_es_invalido():
    errores = validar_contacto("Ana", "300ABC4567", "", "")
    assert "El teléfono debe tener entre 7 y 15 dígitos." in errores


def test_telefono_muy_corto_es_invalido():
    errores = validar_contacto("Ana", "12345", "", "")
    assert "El teléfono debe tener entre 7 y 15 dígitos." in errores


def test_telefono_con_formato_internacional_es_valido():
    assert validar_contacto("Ana", "+57 300 123-4567", "", "") == []


def test_notas_demasiado_largas_son_invalidas():
    errores = validar_contacto("Ana", "", "", "x" * 256)
    assert "Las notas no pueden superar 255 caracteres." in errores


def test_varios_errores_se_reportan_juntos():
    errores = validar_contacto("", "abc", "correo-malo", "")
    assert len(errores) == 3


# --- Normalización usada para detectar duplicados ---

def test_normalizar_telefono_deja_solo_digitos():
    assert normalizar_telefono("+57 (300) 123-4567") == "573001234567"


def test_normalizar_telefono_vacio():
    assert normalizar_telefono("") == ""
    assert normalizar_telefono(None) == ""


def test_normalizar_email_ignora_mayusculas_y_espacios():
    assert normalizar_email("  Ana@Correo.COM ") == "ana@correo.com"
