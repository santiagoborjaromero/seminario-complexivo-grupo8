# main_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import requests
import math 

# Define la clave de la API de TMDB (v3 auth)
TMDB_API_KEY = "c8f4aca1c7dedc6184e0cf3f98e2665e"

# Configura los metadatos de la página (título, ícono, layout)
st.set_page_config(
    page_title="🔥 Dashboard de Recomendación de Películas 🔥",
    page_icon="🎬",#https://docs.streamlit.io/develop/api-reference/navigation/st.page
    layout="wide"
)

st.title("🎬 Dashboard de Recomendación de Películas")

# Define las rutas a los archivos de datos procesados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PROCESS_DIR = os.path.join(BASE_DIR, 'data', 'process')
PROCESSED_FILE = os.path.join(DATA_PROCESS_DIR, 'procesados_movies.csv')
DEFAULT_POSTER = "https://i.imgur.com/7b1hO1V.png"

@st.cache_data
def load_data(file_path):
    """
    Carga el archivo CSV procesado
    Usa @st.cache_data para optimizar el rendimiento y evitar recargas.
    """
    try:
        df = pd.read_csv(file_path, encoding='latin1')
        df['tmdbId'] = pd.to_numeric(df['tmdbId'], errors='coerce')
        return df
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo 'procesados_movies.csv' en {file_path}")
        st.info("Por favor, ejecuta primero el pipeline .")
        return None

@st.cache_data
def get_dynamic_columns(df):
    """
    Extrae las columnas de género (One-Hot) 
    y las de año (Pivot) del DataFrame.
    """
    # Define las columnas base que no son ni géneros ni años.
    base_cols = ['movieid', 'title', 'genres', 'rating_promedio', 'rating_conteo', 'tag', 'tmdbId']
    # Identifica las columnas de año (numéricas de 4 dígitos).
    year_cols = [col for col in df.columns if col.isdigit() and len(col) == 4]
    # Identifica las columnas de género (las restantes).
    genre_cols = [col for col in df.columns if col not in base_cols and col not in year_cols]
    return genre_cols, year_cols

@st.cache_data
def get_poster_url(tmdb_id):
    """
    Llama a la API de TMDB para obtener la URL del póster.
    Usa caché para evitar llamadas duplicadas a la API.
    """
    # Si el tmdbId es nulo (NaN), devuelve el póster por defecto.
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

#  Función principal que ejecuta  Streamlit.
def main():
    df_procesado = load_data(PROCESSED_FILE)
    if df_procesado is None:
        return

    genre_columns, year_columns = get_dynamic_columns(df_procesado)

    #  Crea el panel lateral para los filtros.
    st.sidebar.header("Filtros Interactivos")
    selected_genres = st.sidebar.multiselect(
        "Elige los Géneros:", options=sorted(genre_columns), default=[] 
    )
    rating_slider = st.sidebar.slider(
        "Filtro por Rating Promedio:", 0.0, 5.0, (0.0, 5.0) # tupla (min, max) para definir un rango
    )
    min_ratings_limit = int(df_procesado['rating_conteo'].quantile(0.75))
    total_ratings_slider = st.sidebar.slider(
        "Filtro por Calificaciones:", 0, int(df_procesado['rating_conteo'].max()), min_ratings_limit
    ) 

    # Agrega una sección para seleccionar el orden de los resultados.
    st.sidebar.markdown("---")
    st.sidebar.header("Ordenar Resultados Por:")
    sort_by = st.sidebar.radio(
        "Elegir orden:",
        ["Puntaje (Mejor Calificadas)", "Popularidad (Más Votadas)"],
        index=0 # Por defecto, ordena por Puntaje
    )

    #  Aplica los filtros de la barra lateral al DataFrame.
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
    
    # Ordena el df_filtrado según la selección de 'sort_by'.
    if sort_by == "Popularidad (Más Votadas)":
        df_filtrado = df_filtrado.sort_values(by='rating_conteo', ascending=False)
        sort_label = "Popularidad"
    else: # "Puntaje (Mejor Calificadas)"
        df_filtrado = df_filtrado.sort_values(by='rating_promedio', ascending=False)
        sort_label = "Puntaje"
            
    #  Muestra las métricas principales (KPIs) en la parte superior.
    st.header("Resultados del Filtro")
    col1, col2 = st.columns(2)
    col1.metric("Películas Encontradas", f"{len(df_filtrado):,}")
    col2.metric("Total Películas en BD", f"{len(df_procesado):,}")
    st.markdown("---")
    
    # Crea las dos pestañas Pósteres y Análisis.
    tab_posters, tab_analisis = st.tabs(["🎬 Explorador de Peliculas", "📊 Análisis de Datos"])

    #  Lógica de la Pestaña 1: Explorador de Pósteres.
    with tab_posters:
        st.subheader(f"Top 20 Películas Filtradas (por {sort_label})")
        
        if len(df_filtrado) == 0:
            st.warning("No se encontraron películas con los filtros seleccionados.")
        else:
            # Muestra solo Top 20 para optimizar la carga.
            df_paginado = df_filtrado.head(20) 
            st.markdown(f"Mostrando el **Top 20** (ordenado por {sort_label}) de las **{len(df_filtrado)}** películas encontradas.")
            
            num_cols = 5
            cols = st.columns(num_cols)
            for i, row in enumerate(df_paginado.itertuples()):
                poster_url = get_poster_url(row.tmdbId)
                with cols[i % num_cols]:
                    st.image(poster_url, use_container_width=True, caption=f"{row.rating_promedio:.1f} ⭐ ({row.rating_conteo:,} votos)")
                    
                    # Mantiene el título si es muy largo para mantener para q quede alineado el grid.
                    title = row.title
                    if len(title) > 30:
                        title = title[:30] + "..."
                    
                    # Muestra el título ........
                    st.markdown(f"**{title}**")
                    
                    # Muestra el título  y  detalles.
                    with st.expander("Más detalles"):
                        st.markdown(f"**Título:** {row.title}") # Título completo
                        st.write(f"**Géneros:** {row.genres.replace('|', ', ')}")
                        if pd.notna(row.tag):
                             st.write(f"**Tags:** {str(row.tag)[:100]}...")

    #   Pestaña 2: Gráficos de Análisis.
    with tab_analisis:
        st.subheader("Análisis Adicional de los Datos Filtrados")

        if df_filtrado.empty:
            st.warning("No hay datos para analizar con los filtros seleccionados.")
        else:
            
            #  Gráficos de Popularidad.
            st.subheader("Visualizaciones de Popularidad")
            col_graf1, col_graf2 = st.columns(2)

            with col_graf1:
                st.markdown("#### Top 10 Películas (por N° de Calificaciones)")
                # Este gráfico (Top 10) siempre se ordena por 'rating_conteo' x popularidad.
                df_top10_pop = df_filtrado.nlargest(10, 'rating_conteo')
                fig_bar = px.bar(
                    df_top10_pop, x='rating_conteo', y='title', orientation='h',
                    title='Top 10 Películas más Populares', hover_data=['rating_promedio', 'genres']
                )
                fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_bar, use_container_width=True)

            with col_graf2:
                st.markdown("#### Rating Promedio vs. Popularidad")
                # Este gráfico de dispersión usa el df_filtrado completo.
                fig_scatter = px.scatter(
                    df_filtrado, x='rating_conteo', y='rating_promedio',
                    title='Rating vs. Popularidad', hover_data=['title', 'genres'],
                    color='rating_promedio', size='rating_conteo' 
                )
                st.plotly_chart(fig_scatter, use_container_width=True)

            st.markdown("---")
            # Gráfico usando la matriz pivote de años.
            st.subheader("Evolución del Rating de una Película")
            selected_movie_title = st.selectbox(
                "Selecciona una película para ver su evolución:",
                # Las opciones del selectbox se muestran en el orden seleccionado.
                options=df_filtrado['title'].unique()
            )
            if selected_movie_title:
                movie_data = df_filtrado[df_filtrado['title'] == selected_movie_title].iloc[0]
                evolution_data = movie_data[year_columns][movie_data[year_columns] > 0]
                if not evolution_data.empty:
                    df_evo = pd.DataFrame({'Anio': evolution_data.index.astype(int), 'Rating Promedio': evolution_data.values})
                    fig_line = px.line(df_evo, x='Anio', y='Rating Promedio', title=f"Evolución: {selected_movie_title}", markers=True)
                    st.plotly_chart(fig_line, use_container_width=True)
                else:
                    st.warning(f"No hay datos de evolución de rating para '{selected_movie_title}'.")
            
            st.markdown("---")
            # Tabla de datos detallada al final.
            st.subheader("Datos Filtrados (Detalle)")
            # Esta tabla muestra los datos ordenados según la selección del radio button.
            st.dataframe(df_filtrado, use_container_width=True)


if __name__ == "__main__":
    main()