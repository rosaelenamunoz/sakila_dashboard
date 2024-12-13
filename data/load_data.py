# data/load_data.py
import sqlite3
import pandas as pd

def load_sakila_data():
    try:
        conn = sqlite3.connect('sakila.master.db')  # Asegúrate de que el archivo sakila.db esté en el directorio correcto
        query = "SELECT * FROM film"
        df = pd.read(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
