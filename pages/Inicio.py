import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Configuración inicial de la aplicación
st.set_page_config(page_title="Dashboard Sakila", layout="wide")

# Título y descripción
st.title("Análisis de la Base de Datos Sakila")
st.write("""
Este proyecto analiza los datos de la base de datos **Sakila** para explorar patrones de comportamiento en los alquileres de películas, 
evaluar la popularidad de categorías y títulos, y entender las tendencias de ventas mensuales.
""")

# Conexión a la base de datos y carga de tablas dinámicas
ruta_bd = 'sakila_master.db'
conn = sqlite3.connect(ruta_bd)


# Obtener nombres de todas las tablas disponibles
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tablas = [tabla[0] for tabla in cursor.fetchall()]

# Cargar todas las tablas en un diccionario de DataFrames
datos = {}
for tabla in tablas:
    datos[tabla] = pd.read_sql(f"SELECT * FROM {tabla}", conn)

conn.close()

# Asignar tablas específicas a variables
df_rental = datos['rental']
df_inventory = datos['inventory']
df_film = datos['film']
df_payment = datos['payment']
df_category = datos['category']
df_film_category = datos['film_category']

# Gráfico 1: Número de alquileres por mes
df_rental['rental_date'] = pd.to_datetime(df_rental['rental_date'])
df_rental_by_month = df_rental.groupby(df_rental['rental_date'].dt.to_period('M')).size().reset_index(name='count')
df_rental_by_month['rental_date'] = df_rental_by_month['rental_date'].dt.to_timestamp()

fig1 = px.line(df_rental_by_month, x='rental_date', y='count',
               title='Número de Alquileres por Mes',
               labels={'rental_date': 'Fecha', 'count': 'Cantidad de Alquileres'})
fig1.update_traces(line=dict(color='blue'))

st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Top 10 películas más alquiladas
df_merged = pd.merge(df_inventory, df_film, on='film_id')
df_rental_inventory = pd.merge(df_rental, df_merged, on='inventory_id')
df_top_films = df_rental_inventory.groupby('title')['rental_id'].count().reset_index(name='total_rentals')
df_top_films = df_top_films.sort_values(by='total_rentals', ascending=False).head(10)

fig2 = px.bar(df_top_films, x='title', y='total_rentals',
              title='Top 10 Películas Más Alquiladas',
              labels={'title': 'Título de la Película', 'total_rentals': 'Cantidad de Alquileres'},
              color='total_rentals', color_continuous_scale='Viridis')

st.plotly_chart(fig2, use_container_width=True)

# Gráfico 3: Popularidad de categorías de películas
df_film_category_merged = pd.merge(df_film_category, df_category, on='category_id')
df_rental_film_category = pd.merge(df_rental_inventory, df_film_category_merged, on='film_id')
df_category_popularity = df_rental_film_category.groupby('name')['rental_id'].count().reset_index(name='total_rentals')
df_category_popularity = df_category_popularity.sort_values(by='total_rentals', ascending=False)

fig3 = px.bar(df_category_popularity, x='name', y='total_rentals',
              title='Popularidad de Categorías de Películas',
              labels={'name': 'Categoría', 'total_rentals': 'Cantidad de Alquileres'},
              color='total_rentals', color_continuous_scale='Blues')

st.plotly_chart(fig3, use_container_width=True)

# Gráfico 4: Ventas totales por mes
df_payment['payment_date'] = pd.to_datetime(df_payment['payment_date'])
df_sales_by_month = df_payment.groupby(df_payment['payment_date'].dt.to_period('M'))['amount'].sum().reset_index(name='total_sales')
df_sales_by_month['payment_date'] = df_sales_by_month['payment_date'].dt.to_timestamp()

fig4 = px.line(df_sales_by_month, x='payment_date', y='total_sales',
               title='Ventas Totales por Mes',
               labels={'payment_date': 'Fecha', 'total_sales': 'Monto Total ($)'})
fig4.update_traces(line=dict(color='green'))

st.plotly_chart(fig4, use_container_width=True)

# Mensaje final
st.write("""Estos análisis proporcionan una visión general de los patrones de alquiler y ventas en la base de datos Sakila, 
permitiendo identificar tendencias clave y áreas de oportunidad para optimizar el negocio.""")
