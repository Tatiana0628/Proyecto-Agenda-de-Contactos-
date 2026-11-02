from flask import Flask, render_template, request, redirect, url_for, jsonify
import psycopg2.extras
from db import get_connection, init_db

app = Flask(__name__)


@app.route("/")
@app.route("/buscar", methods=["GET", "POST"])
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
        nombre = request.form["nombre"]
        telefono = request.form.get("telefono", "")
        email = request.form.get("email", "")
        notas = request.form.get("notas", "")
        disponibilidad = request.form.get("disponibilidad", "Disponible") or "Disponible"

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO contactos (nombre, telefono, email, notas, disponibilidad) VALUES (%s, %s, %s, %s, %s);",
            (nombre, telefono, email, notas, disponibilidad),
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index"))

    return render_template("form.html", contacto=None)


@app.route("/edit/<int:contacto_id>", methods=["GET", "POST"])
def edit(contacto_id):
    conn = get_connection()

    if request.method == "POST":
        nombre = request.form["nombre"]
        telefono = request.form.get("telefono", "")
        email = request.form.get("email", "")
        notas = request.form.get("notas", "")
        disponibilidad = request.form.get("disponibilidad", "Disponible") or "Disponible"

        cur = conn.cursor()
        cur.execute(
            "UPDATE contactos SET nombre=%s, telefono=%s, email=%s, notas=%s, disponibilidad=%s WHERE id=%s;",
            (nombre, telefono, email, notas, disponibilidad, contacto_id),
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index"))

    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM contactos WHERE id=%s;", (contacto_id,))
    contacto = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("form.html", contacto=contacto)


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
