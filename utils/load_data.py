import sqlite3
import pandas as pd

def load_sakila_data():
    ruta_bd = "data/sakila_master.db"
    df = pd.read("SELECT * FROM film", conn)
    conn.close()
    return df


