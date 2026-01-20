# Bibliotecas
from datetime import datetime
from flask import Flask, render_template, abort
from data.pymes import pymes
import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)


# Ubicación
app = Flask(__name__)
app.secret_key = "jacobo-perdigon-producto" 

# Conexión y preparación base de datos
def conectar_db():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id SERIAL PRIMARY KEY,
            fecha TIMESTAMP NOT NULL,
            pagina TEXT
        );
    """)

    conn.commit()
    return conn, cursor


# Registro de hora por ingreso
from datetime import datetime, timedelta
from flask import session
import psycopg2
import os

def guardar_ingreso(pagina="index"):
    ahora = datetime.now()

    # Creamos el diccionario si no existe
    if "ultima_visita" not in session:
        session["ultima_visita"] = {}

    # Evitar duplicados por página (5 minutos)
    if pagina in session["ultima_visita"]:
        ultima = datetime.fromisoformat(session["ultima_visita"][pagina])
        if ahora - ultima < timedelta(minutes=5):
            return

    # Guardamos la hora de esta página
    session["ultima_visita"][pagina] = ahora.isoformat()

    # Guardar en la DB
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO registros (fecha, pagina) VALUES (%s, %s)",
        (ahora, pagina)
    )
    conn.commit()
    conn.close()


    
    # Guardar el momento del registro en la sesión
    session["ultima_visita"] = ahora.isoformat()

# Rutas
@app.route("/")
def ingreso():
    guardar_ingreso("index")
    return render_template("index.html", pymes=pymes)

@app.route("/promo")
def ingreso_promo():
    guardar_ingreso("promo")
    return render_template("promo.html")

@app.route("/pyme/<int:pyme_id>")
def pyme(pyme_id):
    for p in pymes:
        if p["id"] == pyme_id:
            guardar_ingreso(f"pyme-{pyme_id}")
            return render_template(
                "pyme.html",
                pyme=p,
                productos = p["productos"]
                )
    abort(404)


# Conectar y crear tabla al iniciar la app
conn, cursor = conectar_db()
conn.close()

# Solo para correr localmente
if __name__ == "__main__":
    app.run(debug=True)

    
    app.run(debug=True)
