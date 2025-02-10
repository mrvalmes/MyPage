from flask import Flask, render_template, url_for
import sqlite3


app = Flask(__name__)


@app.route("/")
def index():
    # Renderiza tu archivo index.html (que ahora está en templates/)
    return render_template("index.html")


@app.route("/home")
def home():   
    # Renderiza reportes.html
    return render_template("Home.html")


@app.route("/dashboard")
def dashboard():
    # Conectar a BD
    # conn = sqlite3.connect("ruta_de_tu_basedatos.db")
    # cursor = conn.cursor()
    # Hacer consulta
    # cursor.execute("SELECT * FROM transacciones LIMIT 10")
    # rows = cursor.fetchall()
    # conn.close()
    # Renderiza ventas.html
    # return render_template("Dashb.html", datos=rows)
    return render_template("dashboard.html")


if __name__ == "__main__":
    # debug=True para desarrollo
    app.run(debug=True)
