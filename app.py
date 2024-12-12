import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from data.load_data import load_sakila_data

# Configuración inicial
st.set_page_config(page_title="Dashboard Sakila", layout="wide")

# Título de la app
st.title("Análisis de la Base de Datos Sakila")
st.markdown("""
## Rosaelena Muñoz Ugalde
## Proyecto Final
## Este dashboard Interactivo permite analizar y visualizar datos sobre el comportamiento de los alquileres de películas.
""")

# Agregar una imagen local desde la carpeta 'assets/images/'
st.image("/Users/rosaelenamunoz/Documents/sakila_dashboard/imagen.png")
