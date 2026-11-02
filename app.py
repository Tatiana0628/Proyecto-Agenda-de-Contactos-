from flask import Flask, render_template, request, redirect, url_for, jsonify
import psycopg2.extras
from db import get_connection, init_db, buscar_duplicados
from validaciones import validar_contacto

app = Flask(__name__)


def leer_formulario(origen=None):
    origen = origen if origen is not None else request.form
    return {
        "nombre": str(origen.get("nombre") or "").strip(),
        "telefono": str(origen.get("telefono") or "").strip(),
        "email": str(origen.get("email") or "").strip(),
        "notas": str(origen.get("notas") or "").strip(),
        "disponibilidad": str(origen.get("disponibilidad") or "Disponible").strip(),
    }


def validar_datos(datos, excluir_id=None):
    """Funcionalidad nueva 2: valida formato y duplicados. Devuelve (errores, código HTTP).

    400 = datos con formato inválido, 409 = teléfono o email duplicado.
    """
    errores = validar_contacto(datos["nombre"], datos["telefono"], datos["email"], datos["notas"])
    if errores:
        return errores, 400
    errores = buscar_duplicados(datos["telefono"], datos["email"], excluir_id)
    if errores:
        return errores, 409
    return [], 200


@app.route("/")
def index():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        disponibilidad = request.form.get("disponibilidad", "").strip()
    else:
        nombre = request.args.get("nombre", request.args.get("q", "")).strip()
        disponibilidad = request.args.get("disponibilidad", "").strip()

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    query = "SELECT * FROM contactos WHERE 1=1"
    params = []

    if nombre:
        query += " AND nombre ILIKE %s"
        params.append(f"%{nombre}%")

    if disponibilidad and disponibilidad.lower() not in ["todas", "todos"]:
        query += " AND disponibilidad = %s"
        params.append(disponibilidad)

    query += " ORDER BY id DESC;"

    cur.execute(query, tuple(params))
    contactos = cur.fetchall()
    cur.close()
    conn.close()

    if (
        request.is_json
        or request.headers.get("Accept") == "application/json"
        or request.args.get("format") == "json"
    ):
        return jsonify(contactos)

    return render_template(
        "index.html",
        contactos=contactos,
        nombre_query=nombre,
        disponibilidad_filter=disponibilidad,
    )


# /buscar usa la misma vista que "/", pero como endpoint aparte: así redirect(url_for("index"))
# después de guardar o eliminar (peticiones POST) sigue llevando a "/" y no a "/buscar".
app.add_url_rule("/buscar", "buscar", index, methods=["GET", "POST"])


@app.route("/api/buscar", methods=["GET"])
@app.route("/api/contactos", methods=["GET"])
def api_buscar():
    nombre = request.args.get("nombre", request.args.get("q", "")).strip()
    disponibilidad = request.args.get("disponibilidad", "").strip()

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    query = "SELECT * FROM contactos WHERE 1=1"
    params = []

    if nombre:
        query += " AND nombre ILIKE %s"
        params.append(f"%{nombre}%")

    if disponibilidad and disponibilidad.lower() not in ["todas", "todos"]:
        query += " AND disponibilidad = %s"
        params.append(disponibilidad)

    query += " ORDER BY id DESC;"

    cur.execute(query, tuple(params))
    contactos = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(contactos)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        datos = leer_formulario()
        errores, codigo = validar_datos(datos)
        if errores:
            return render_template("form.html", contacto=None, datos=datos, errores=errores), codigo

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO contactos (nombre, telefono, email, notas, disponibilidad) VALUES (%s, %s, %s, %s, %s);",
            (datos["nombre"], datos["telefono"], datos["email"], datos["notas"], datos["disponibilidad"]),
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index"))

    return render_template("form.html", contacto=None, datos=None, errores=[])


@app.route("/edit/<int:contacto_id>", methods=["GET", "POST"])
def edit(contacto_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM contactos WHERE id=%s;", (contacto_id,))
    contacto = cur.fetchone()

    if contacto is None:
        cur.close()
        conn.close()
        return "Contacto no encontrado", 404

    if request.method == "POST":
        datos = leer_formulario()
        errores, codigo = validar_datos(datos, excluir_id=contacto_id)
        if errores:
            cur.close()
            conn.close()
            return render_template("form.html", contacto=contacto, datos=datos, errores=errores), codigo

        cur.execute(
            "UPDATE contactos SET nombre=%s, telefono=%s, email=%s, notas=%s, disponibilidad=%s WHERE id=%s;",
            (datos["nombre"], datos["telefono"], datos["email"], datos["notas"], datos["disponibilidad"], contacto_id),
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index"))

    cur.close()
    conn.close()
    return render_template("form.html", contacto=contacto, datos=contacto, errores=[])


@app.route("/api/validar-contacto", methods=["POST"])
def api_validar_contacto():
    """Valida un contacto sin guardarlo. Lo usa el formulario para mostrar errores mientras se escribe.

    Recibe JSON {nombre, telefono, email, notas, id?} y responde {valido, errores}.
    """
    cuerpo = request.get_json(silent=True) or {}
    datos = leer_formulario(cuerpo)
    excluir_id = cuerpo.get("id")
    try:
        excluir_id = int(excluir_id) if excluir_id else None
    except (TypeError, ValueError):
        excluir_id = None
    errores, _ = validar_datos(datos, excluir_id)
    return jsonify({"valido": not errores, "errores": errores})


@app.route("/delete/<int:contacto_id>", methods=["POST"])
def delete(contacto_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM contactos WHERE id=%s;", (contacto_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
else:
    init_db()
