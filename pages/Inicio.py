import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from data.load_data import load_sakila_data

# Configuración inicial
st.set_page_config(page_title="Dashboard Sakila", layout="wide")

# Título de la app
st.title("Dashboard de Alquileres - Base de Datos Sakila")


# Conexión a la base de datos y carga de datos
def load_data():
    conn = sqlite3.connect('sakila_master.db')
    
    try:
        df_rental = pd.read_sql('SELECT * FROM rental', conn)
        df_inventory = pd.read_sql('SELECT * FROM inventory', conn)
        df_film = pd.read_sql('SELECT * FROM film', conn)
        df_payment = pd.read_sql('SELECT * FROM payment', conn)
        df_actor = pd.read_sql('SELECT * FROM film_actor', conn)
        df_category = pd.read_sql('SELECT * FROM category', conn)
        df_film_category = pd.read_sql('SELECT * FROM film_category', conn)
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
    finally:
        conn.close()
    
    return df_rental, df_inventory, df_film, df_payment, df_actor, df_category, df_film_category

df_rental, df_inventory, df_film, df_payment, df_actor, df_category, df_film_category = load_data()

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

# Tarjeta 2: Resumen de Alquileres por Película
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

# Gráfico 1: Número de Alquileres por Mes
df_rental['rental_date'] = pd.to_datetime(df_rental['rental_date'])
df_rental_by_month = df_rental.groupby(df_rental['rental_date'].dt.to_period('M')).size().reset_index(name='count')
df_rental_by_month['rental_date'] = df_rental_by_month['rental_date'].dt.to_timestamp()

fig1 = px.line(df_rental_by_month, x='rental_date', y='count', title='Número de Alquileres por Mes', line_shape='spline')
fig1.update_traces(line=dict(color='royalblue'))

# Gráfico 2: Popularidad de Categorías de Películas
df_film_category_merged = pd.merge(df_film_category, df_category, on='category_id')
df_rental_category = pd.merge(df_rental_inventory, df_film_category_merged, on='film_id')

# Filtrar por categorías seleccionadas
if category_filter:
    df_rental_category = df_rental_category[df_rental_category['name'].isin(category_filter)]

df_category_popularity = df_rental_category.groupby('name')['rental_id'].count().reset_index(name='total_rentals')
df_category_popularity = df_category_popularity.sort_values(by='total_rentals', ascending=False)

fig2 = px.bar(df_category_popularity, x='name', y='total_rentals', title='Popularidad de Categorías de Películas', color='total_rentals', color_continuous_scale='Jet')
fig2.update_layout(xaxis_tickangle=-45)

# Gráfico 3: Ventas Totales por Mes
df_payment['payment_date'] = pd.to_datetime(df_payment['payment_date'])
df_sales_by_month = df_payment.groupby(df_payment['payment_date'].dt.to_period('M'))['amount'].sum().reset_index(name='total_sales')
df_sales_by_month['payment_date'] = df_sales_by_month['payment_date'].dt.to_timestamp()

fig3 = px.line(df_sales_by_month, x='payment_date', y='total_sales', title='Ventas Totales por Mes', line_shape='spline')
fig3.update_traces(line=dict(color='darkorange'))

# Disposición de gráficos
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig1)

with col2:
    st.plotly_chart(fig2)

st.plotly_chart(fig3)
