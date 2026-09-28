from flask import Flask, render_template, request, redirect, url_for
import psycopg2.extras
from db import get_connection, init_db

app = Flask(__name__)


@app.route("/")
def index():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM contactos ORDER BY id DESC;")
    contactos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", contactos=contactos)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        nombre = request.form["nombre"]
        telefono = request.form.get("telefono", "")
        email = request.form.get("email", "")
        notas = request.form.get("notas", "")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO contactos (nombre, telefono, email, notas) VALUES (%s, %s, %s, %s);",
            (nombre, telefono, email, notas),
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

        cur = conn.cursor()
        cur.execute(
            "UPDATE contactos SET nombre=%s, telefono=%s, email=%s, notas=%s WHERE id=%s;",
            (nombre, telefono, email, notas, contacto_id),
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
