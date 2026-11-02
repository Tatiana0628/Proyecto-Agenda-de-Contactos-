import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TELEFONO_REGEX = re.compile(r"^\+?[0-9 ()-]+$")


def normalizar_telefono(telefono):
    """Deja solo los dígitos: '+57 300-123 4567' -> '573001234567'."""
    return re.sub(r"\D", "", telefono or "")


def normalizar_email(email):
    """Quita espacios y pasa a minúsculas para comparar emails."""
    return (email or "").strip().lower()


def validar_contacto(nombre, telefono, email, notas):
    """Devuelve una lista de mensajes de error. Lista vacía = datos válidos."""
    errores = []
    nombre = (nombre or "").strip()
    telefono = (telefono or "").strip()
    email = (email or "").strip()
    notas = (notas or "").strip()

    if not nombre:
        errores.append("El nombre es obligatorio.")
    elif len(nombre) > 100:
        errores.append("El nombre no puede superar 100 caracteres.")

    if telefono:
        digitos = normalizar_telefono(telefono)
        if not TELEFONO_REGEX.match(telefono) or not 7 <= len(digitos) <= 15:
            errores.append("El teléfono debe tener entre 7 y 15 dígitos.")

    if email:
        if len(email) > 100 or not EMAIL_REGEX.match(email):
            errores.append("El email no tiene un formato válido.")

    if len(notas) > 255:
        errores.append("Las notas no pueden superar 255 caracteres.")

    return errores
