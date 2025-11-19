# dashboard/analisis.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
# Importa las funciones helper desde tu script de funciones
from dashboard.funciones import load_data, get_dynamic_columns, get_poster_url, api, apiPost

st.title("📊 Análisis de Datos")
st.markdown("Análisis interactivo del catálogo de películas.")

# --------------------------------------
# Genres, consulta (para el filtro)
# --------------------------------------
@st.cache_data
def load_genres():
    resp_genres = api("/data/genres")
    if resp_genres and resp_genres.get("status", False):
        genre_data = json.loads(resp_genres.get("data", "[]"))
        return [gen["genre"] for gen in genre_data]
    return []

genre_columns = load_genres()
if not genre_columns:
    st.error("No se pudieron cargar los géneros desde la API. No se puede continuar.")
    st.stop()
    
# --------------------------------------
# Objetos (Barra Lateral de Filtros)
# --------------------------------------
st.sidebar.title("Análisis de Datos")
st.sidebar.header("Filtros Interactivos")
selected_genres = st.sidebar.multiselect(
    "Elige los Géneros:", options=sorted(genre_columns), default=[] 
)
count_slider = st.sidebar.slider(
    "Popularidad en votos:", 0, 70000, (1000, 70000) # tupla (min, max) para definir un rango
)
rating_slider = st.sidebar.slider(
    "Filtro por Rating Promedio:", 0.0, 5.0, (0.0, 5.0) 
)

# Agrega una sección para seleccionar el orden de los resultados.
st.sidebar.markdown("---")
st.sidebar.header("Ordenar Resultados Por:")
sort_by = st.sidebar.radio(
    "Elegir orden:",
    ["Rating", "Popularidad"],
    index=1 # Por defecto, ordena por Popularidad
)
sort_label = "Popularidad" if sort_by == "Popularidad" else "Rating"

parameters = {
    "order_by": sort_label, # Pasa el nuevo valor de orden
    "genres": selected_genres,
    "rating_min": rating_slider[0],
    "rating_max": rating_slider[1],
    "items_per_page": 100000, # Trae todos los datos que coincidan
    "count_slider_min": count_slider[0],
    "count_slider_max": count_slider[1],
    "movie_title": ""
}

# --------------------------------------
# Trae el listado de Movies con los filtros seleccionados 
# --------------------------------------
resp_movies = apiPost("/data/clean_movies", parameters)


status = resp_movies.get("status", False)
message = resp_movies.get("message", "") # Usar "" como default

if status == False:
    st.warning("La lista de películas está vacia o la API falló.")
    st.error(f"Mensaje de la API: {message}")
    st.stop() # Detener si no hay datos

df_procesado_json = json.loads(resp_movies.get("data", "[]"))
col_categoricas = message.split(",")


df_filtrado = pd.DataFrame(df_procesado_json, columns=col_categoricas)

# --- Feature Engineering (Hecho en el Dashboard) ---
df_filtrado['release_year'] = df_filtrado['title'].str.extract(r'\((\d{4})\)')
df_filtrado['release_year'] = pd.to_numeric(df_filtrado['release_year'], errors='coerce')

# Llama a la función helper para obtener las listas de columnas
genre_columns_dynamic, year_columns = get_dynamic_columns(df_filtrado)

#  Muestra las métricas principales (KPIs) en la parte superior.
st.header("Resultados del Filtro")
col1, col2 = st.columns(2)
col1.metric("Películas Encontradas", f"{len(df_filtrado):,}")
col2.metric("Total Películas en BD", "27,278") # Valor hardcodeado del total
st.markdown("---")

# --- Inicio del Área de Gráficos ---
if df_filtrado.empty:
    st.warning("No hay datos para analizar con los filtros seleccionados.")
else:
    
    # --- Gráficos Agregados ---
    st.subheader("Análisis Géneros y Años")
    
    df_genres_melted = df_filtrado.melt(
        id_vars=['movieid', 'title', 'rating_promedio', 'rating_conteo'], 
        value_vars=genre_columns_dynamic, 
        var_name='genre', 
        value_name='is_genre'
    )
    df_genres_melted = df_genres_melted[df_genres_melted['is_genre'] == 1]
    
    df_genre_stats = df_genres_melted.groupby('genre').agg(
        rating_promedio_genero=('rating_promedio', 'mean'),
        total_peliculas=('movieid', 'count')
    ).reset_index().sort_values(by='total_peliculas', ascending=False)
    
    col_agg_1, col_agg_2 = st.columns(2)

    with col_agg_1:
        # 1. Gráfico de Géneros 
        st.markdown("#### Distribución de Géneros (Treemap)")
        fig_treemap = px.treemap(
            df_genre_stats.head(20), 
            path=[px.Constant('Géneros'), 'genre'], 
            values='total_peliculas',
            color='rating_promedio_genero',
            color_continuous_scale='YlOrRd', 
            title='Proporción de Géneros (Tamaño=Conteo, Color=Rating)',
            hover_data={'rating_promedio_genero': ':.2f'}
        )
        fig_treemap.update_layout(margin = dict(t=50, l=25, r=25, b=25))
        st.plotly_chart(fig_treemap, use_container_width=True)

    with col_agg_2:
        # 2. Gráfico de Año de Estreno 
        st.markdown("#### Distribución por Año de Estreno")
        df_year_filtered = df_filtrado.dropna(subset=['release_year'])
        df_year_filtered['release_year'] = df_year_filtered['release_year'].astype(int)
        
        fig_hist_year = px.histogram(
            df_year_filtered,
            x='release_year',
            nbins=50, 
            title='Conteo de Películas por Año de Estreno'
        )
        st.plotly_chart(fig_hist_year, use_container_width=True)

    st.markdown("---")
    
    # --- Gráficos de Distribución ---
    st.subheader("Análisis de Distribución de Ratings")
    col_dist_1, col_dist_2 = st.columns(2)
    
    with col_dist_1:
        # 3. Gráfico de Barras 
        st.markdown("#### Rating Promedio por Género (Top 15)")
        df_genre_ratings = df_genre_stats.nlargest(15, 'total_peliculas').sort_values(by='rating_promedio_genero', ascending=False)

        fig_bar_rating = px.bar(
            df_genre_ratings,
            x='genre',
            y='rating_promedio_genero',
            color='genre', 
            title='Rating Promedio por Género (Top 15 Populares)',
            labels={'rating_promedio_genero': 'Rating Promedio (1-5)'}
        )
        fig_bar_rating.update_yaxes(range=[0, 5])
        st.plotly_chart(fig_bar_rating, use_container_width=True)
            
    with col_dist_2:
        # 4. Gráfico (Rating vs. Popularidad)
        st.markdown("#### Rating Promedio vs. Popularidad")
        fig_scatter = px.scatter(
            df_filtrado, x='rating_conteo', y='rating_promedio',
            title='Rating vs. Popularidad', 
            hover_data=['title', 'genres'],
            color='rating_promedio', 
            size='rating_conteo',
            opacity=0.6,
            labels={'rating_conteo': 'Popularidad (N° Votos)', 'rating_promedio': 'Rating Promedio (Calidad)'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.markdown("---")
    
    #  Gráficos de Popularidad 
    st.subheader("Visualizaciones de Popularidad (Top 10)")
    
    df_top10_pop = df_filtrado.nlargest(10, 'rating_conteo')
    fig_bar = px.bar(
        df_top10_pop, x='rating_conteo', y='title', orientation='h',
        title='Top 10 Películas más Populares (por Votos)', hover_data=['rating_promedio', 'genres']
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    # Gráfico usando la matriz pivote de años.
    st.subheader(f"Evolución del Rating del Top 10 (por {sort_label})")
    
    df_top10 = df_filtrado.head(10)
    
    df_top10_melted = df_top10.melt(
        id_vars=['movieid', 'title'],
        value_vars=year_columns,
        var_name='Anio',
        value_name='Rating Anual'
    )
    
    df_top10_melted = df_top10_melted[df_top10_melted['Rating Anual'] > 0]
    df_top10_melted['Anio'] = df_top10_melted['Anio'].astype(int)
    
    if not df_top10_melted.empty:
        fig_line = px.line(
            df_top10_melted, 
            x='Anio', 
            y='Rating Anual', 
            color='title', 
            title=f"Evolución del Rating del Top 10 (por {sort_label})", 
            markers=True
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning(f"No hay datos de evolución de rating para el Top 10 seleccionado.")

    st.markdown("---")
    # Tabla de datos detallada
    st.subheader("Datos Filtrados (Detalle)")
    

    columnas = ["title", "rating_conteo", "genres", "tag"]
    newdf = pd.DataFrame(df_filtrado, columns=columnas)
    
    column_configuration = {
        "title": st.column_config.TextColumn("Titulo", help="Titulo de la Pelicula", max_chars=100, width="medium"),
        "rating_conteo": st.column_config.TextColumn("Votos", help="Votos en total", max_chars=20, width="small"),
        "genres": st.column_config.TextColumn("Generos", help="Generos de la Pelicula", max_chars=100, width="medium"),
        "tag": st.column_config.TextColumn("Tag", help="Tags de la Pelicula", max_chars=100, width="medium"),
    }
    
    st.dataframe(newdf.head(10), column_config=column_configuration, hide_index=True, width='stretch')
