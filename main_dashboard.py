# main_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import requests
import math # Necesario para la paginación

# --- Uso del API DE TMDB  https://www.themoviedb.org/settings/api---
TMDB_API_KEY = "c8f4aca1c7dedc6184e0cf3f98e2665e"
# ------------------------------------

# --- Configuración de la Página ---
st.set_page_config(
    page_title="🔥 Dashboard de Recomendación de Películas 🔥",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Dashboard de Recomendación de Películas")

#  Definición de Rutas 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PROCESS_DIR = os.path.join(BASE_DIR, 'data', 'process')
PROCESSED_FILE = os.path.join(DATA_PROCESS_DIR, 'procesados_movies.csv')
DEFAULT_POSTER = "https://i.imgur.com/7b1hO1V.png"

# Funciones de Carga 

@st.cache_data
def load_data(file_path):
    """ Carga el archivo CSV procesado de tu Fase 1. """
    try:
        df = pd.read_csv(file_path, encoding='latin1')
        df['tmdbId'] = pd.to_numeric(df['tmdbId'], errors='coerce')
        return df
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo 'procesados_movies.csv' en {file_path}")
        st.info("Por favor, ejecuta primero el pipeline de la Fase 1 (actualizado con link.csv).")
        return None

@st.cache_data
def get_dynamic_columns(df):
    """ Extrae dinámicamente las columnas de género (One-Hot) y las de año (Pivot) """
    # Corregido: usa 'tag' en lugar de 'tags_agrupados'
    base_cols = ['movieid', 'title', 'genres', 'rating_promedio', 'rating_conteo', 'tag', 'tmdbId']
    year_cols = [col for col in df.columns if col.isdigit() and len(col) == 4]
    genre_cols = [col for col in df.columns if col not in base_cols and col not in year_cols]
    return genre_cols, year_cols

@st.cache_data
def get_poster_url(tmdb_id):
    """ Llama a la API de TMDB para obtener la URL del póster. """
    
    # --- ¡CORRECCIÓN 3! ---
    # El bug estaba aquí. Se comparaba la clave con un placeholder.
    # Ahora solo comprueba si el tmdb_id es nulo.
    if pd.isna(tmdb_id):
        return DEFAULT_POSTER
        
    url = f"https://api.themoviedb.org/3/movie/{int(tmdb_id)}?api_key={TMDB_API_KEY}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("poster_path"):
            return f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
        else:
            return DEFAULT_POSTER
    except requests.exceptions.RequestException:
        return DEFAULT_POSTER

#  Función Principal 
def main():
    df_procesado = load_data(PROCESSED_FILE)
    if df_procesado is None:
        return

    genre_columns, year_columns = get_dynamic_columns(df_procesado)

    #  Barra Lateral Filtros
    st.sidebar.header("Filtros Interactivos")
    selected_genres = st.sidebar.multiselect(
        "Elige los Géneros:", options=sorted(genre_columns), default=[] 
    )
    rating_slider = st.sidebar.slider(
        "Filtro por Rating Promedio:", 0.0, 5.0, (0.0, 5.0)
    )
    min_ratings_limit = int(df_procesado['rating_conteo'].quantile(0.75))
    total_ratings_slider = st.sidebar.slider(
        "Filtro por Calificaciones:", 0, int(df_procesado['rating_conteo'].max()), min_ratings_limit
    ) 

    #  Filtrado del DataFrame
    df_filtrado = df_procesado.copy()
    df_filtrado = df_filtrado[
        (df_filtrado['rating_promedio'] >= rating_slider[0]) &
        (df_filtrado['rating_promedio'] <= rating_slider[1])
    ]
    df_filtrado = df_filtrado[
        df_filtrado['rating_conteo'] >= total_ratings_slider
    ]
    if selected_genres:
        for genre in selected_genres:
            df_filtrado = df_filtrado[df_filtrado[genre] == 1]
    
    # Ordenar por popularidad por defecto (para la paginación)
    df_filtrado = df_filtrado.sort_values(by='rating_conteo', ascending=False)
            
    #  Visualización (Métricas Globales) 
    st.header("Resultados del Filtro")
    col1, col2 = st.columns(2)
    col1.metric("Películas Encontradas", f"{len(df_filtrado):,}")
    col2.metric("Total Películas en BD", f"{len(df_procesado):,}")
    st.markdown("---")
    
    # --- Creación de Pestañas ---
    tab_posters, tab_analisis = st.tabs(["🎬 Explorador de Pósteres", "📊 Análisis de Datos"])

    #  Pestaña 1:  Pósters (CON PAGINACIÓN)
    with tab_posters:
        st.subheader("Películas Filtradas (Vista de Póster)")
        
        if len(df_filtrado) == 0:
            st.warning("No se encontraron películas con los filtros seleccionados.")
        else:
            # --- LÓGICA DE PAGINACIÓN ---
            items_per_page = 20 # 5 columnas x 4 filas
            total_items = len(df_filtrado)
            total_pages = max(1, math.ceil(total_items / items_per_page))
            
            page = st.number_input("Página", min_value=1, max_value=total_pages, value=1, step=1)
            
            st.markdown(f"Mostrando página **{page}** de **{total_pages}**")
            
            start_idx = (page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, total_items)
            
            df_paginado = df_filtrado.iloc[start_idx:end_idx]
            # --- FIN LÓGICA DE PAGINACIÓN ---
            
            num_cols = 5
            cols = st.columns(num_cols)
            for i, row in enumerate(df_paginado.itertuples()):
                poster_url = get_poster_url(row.tmdbId)
                with cols[i % num_cols]:
                    # Corregido: usa use_column_width='always'
                    st.image(poster_url, use_column_width='always', caption=f"{row.rating_promedio:.1f} ⭐ ({row.rating_conteo:,} votos)")
                    st.markdown(f"**{row.title}**")
                    with st.expander("Más detalles"):
                        st.write(f"**Géneros:** {row.genres.replace('|', ', ')}")
                        # Corregido: usa 'row.tag' y comprueba si es nulo (pd.notna)
                        if pd.notna(row.tag):
                             st.write(f"**Tags:** {str(row.tag)[:100]}...")

    #  Pestaña 2: GráfICOS de Análisis (COMPLETA)
    with tab_analisis:
        st.subheader("Análisis Adicional de los Datos Filtrados")

        if df_filtrado.empty:
            st.warning("No hay datos para analizar con los filtros seleccionados.")
        else:
            
            # --- Gráficos de Popularidad ---
            st.subheader("Visualizaciones de Popularidad")
            col_graf1, col_graf2 = st.columns(2)

            with col_graf1:
                st.markdown("#### Top 10 Películas (por N° de Calificaciones)")
                df_top10 = df_filtrado.nlargest(10, 'rating_conteo')
                fig_bar = px.bar(
                    df_top10, x='rating_conteo', y='title', orientation='h',
                    title='Top 10 Películas más Populares', hover_data=['rating_promedio', 'genres']
                )
                fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_bar, use_container_width=True) # Corregido: usa use_container_width

            with col_graf2:
                st.markdown("#### Rating Promedio vs. Popularidad")
                fig_scatter = px.scatter(
                    df_filtrado, x='rating_conteo', y='rating_promedio',
                    title='Rating vs. Popularidad', hover_data=['title', 'genres'],
                    color='rating_promedio', size='rating_conteo' 
                )
                st.plotly_chart(fig_scatter, use_container_width=True) # Corregido: usa use_container_width

            st.markdown("---")
            # Gráfico de Evolución 
            st.subheader("Evolución del Rating de una Película")
            selected_movie_title = st.selectbox(
                "Selecciona una película para ver su evolución:",
                options=df_filtrado['title'].unique()
            )
            if selected_movie_title:
                movie_data = df_filtrado[df_filtrado['title'] == selected_movie_title].iloc[0]
                evolution_data = movie_data[year_columns][movie_data[year_columns] > 0]
                if not evolution_data.empty:
                    df_evo = pd.DataFrame({'Anio': evolution_data.index.astype(int), 'Rating Promedio': evolution_data.values})
                    fig_line = px.line(df_evo, x='Anio', y='Rating Promedio', title=f"Evolución: {selected_movie_title}", markers=True)
                    st.plotly_chart(fig_line, use_container_width=True) # Corregido: usa use_container_width
                else:
                    st.warning(f"No hay datos de evolución de rating para '{selected_movie_title}'.")
            
            st.markdown("---")
            # Tabla de Datos
            st.subheader("Datos Filtrados (Detalle)")
            st.dataframe(df_filtrado, use_container_width=True) # Corregido: usa use_container_width

# Este bloque SIEMPRE debe ir al final
if __name__ == "__main__":
    main()