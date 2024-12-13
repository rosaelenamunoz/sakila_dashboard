import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Configuración inicial de la aplicación
st.set_page_config(page_title="Dashboard Sakila", layout="wide")

# Título y descripción
st.title("Dashboard de la base de datos Sakila")
st.write("""
Este proyecto analiza los datos de la base de datos **Sakila** para explorar patrones de comportamiento en los alquileres de películas, 
evaluar la popularidad de categorías y títulos, y entender las tendencias de ventas mensuales.
""")

# Conexión a la base de datos y carga de tablas dinámicas
ruta_bd = 'sakila_master.db'
conn = sqlite3.connect(ruta_bd)

# Asignar tablas específicas a variables
df_rental = pd.read_sql("SELECT * FROM rental", conn)
df_inventory = pd.read_sql("SELECT * FROM inventory", conn)
df_film = pd.read_sql("SELECT * FROM film", conn)
df_payment = pd.read_sql("SELECT * FROM payment", conn)
df_category = pd.read_sql("SELECT * FROM category", conn)
df_film_category = pd.read_sql("SELECT * FROM film_category", conn)

conn.close()

# Filtros en la barra lateral
st.sidebar.header('Filtros')
rental_date_filter = st.sidebar.date_input('Selecciona una fecha', value=pd.to_datetime("2022-01-01"))
category_filter = st.sidebar.multiselect('Selecciona las categorías', options=df_category['name'].unique())
film_filter = st.sidebar.multiselect('Selecciona las películas', options=df_film['title'].unique())

# Tarjeta 1: Información general
with st.expander("Estadísticas Generales"):
    total_peliculas = df_film.shape[0]
    total_alquileres = df_rental.shape[0]
    total_ventas = df_payment['amount'].sum()

    st.write(f"**Total de Películas**: {total_peliculas}")
    st.write(f"**Total de Alquileres**: {total_alquileres}")
    st.write(f"**Ventas Totales**: ${total_ventas:,.2f}")

# Resumen de Alquileres por Película
with st.expander("Resumen de Alquileres por Película"):
    df_merged = pd.merge(df_inventory, df_film, on='film_id')
    df_rental_inventory = pd.merge(df_rental, df_merged, on='inventory_id')
    
    # Filtrar por las películas seleccionadas
    if film_filter:
        df_rental_inventory = df_rental_inventory[df_rental_inventory['title'].isin(film_filter)]
    
    # Top 10 películas más alquiladas
    df_top_films = df_rental_inventory.groupby('title')['rental_id'].count().reset_index(name='total_rentals')
    df_top_films = df_top_films.sort_values(by='total_rentals', ascending=False).head(10)

    st.write(df_top_films)

# Gráfico 1: Número de alquileres por mes
df_rental['rental_date'] = pd.to_datetime(df_rental['rental_date'])
df_rental_by_month = df_rental.groupby(df_rental['rental_date'].dt.to_period('M')).size().reset_index(name='count')
df_rental_by_month['rental_date'] = df_rental_by_month['rental_date'].dt.to_timestamp()

fig1 = px.line(df_rental_by_month, x='rental_date', y='count',
               title='Número de Alquileres por Mes',
               labels={'rental_date': 'Fecha', 'count': 'Cantidad de Alquileres'})
fig1.update_traces(line=dict(color='blue'))

st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Popularidad de categorías de películas
df_film_category_merged = pd.merge(df_film_category, df_category, on='category_id')
df_rental_film_category = pd.merge(df_rental_inventory, df_film_category_merged, on='film_id')
df_category_popularity = df_rental_film_category.groupby('name')['rental_id'].count().reset_index(name='total_rentals')
df_category_popularity = df_category_popularity.sort_values(by='total_rentals', ascending=False)

fig2 = px.bar(df_category_popularity, x='name', y='total_rentals',
              title='Popularidad de Categorías de Películas',
              labels={'name': 'Categoría', 'total_rentals': 'Cantidad de Alquileres'},
              color='total_rentals', color_continuous_scale='Blues')

st.plotly_chart(fig2, use_container_width=True)

# Mensaje final
st.write("""Estos análisis proporcionan una visión general de los patrones de alquiler y ventas en la base de datos Sakila, 
permitiendo identificar tendencias clave y áreas de oportunidad para optimizar el negocio.""")
