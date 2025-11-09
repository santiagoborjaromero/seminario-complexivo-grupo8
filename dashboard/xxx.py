import streamlit as st
import pandas as pd
import plotly.express as px
import os
import requests
import json

from dashboard.funciones import load_data, get_dynamic_columns, get_poster_url, api, apiPost

# Configura los metadatos de la página (título, ícono, layout)
st.set_page_config(
    page_title="🔥 Películas mas puntuadas en toda la historia 🔥",
    page_icon="🎬",#https://docs.streamlit.io/develop/api-reference/navigation/st.page
    layout="wide"
)

# Define las rutas a los archivos de datos procesados
BASE_DIR = os.getcwd() 
# PROCESSED_FILE = os.path.join(BASE_DIR, 'data', 'process', 'procesados_movies.csv')
DEFAULT_POSTER = os.path.join(BASE_DIR, 'images', 'default.png')
API_BASE_URL = "http://localhost:8000"
ITEMS_PER_PAGE = 10

#  Función principal que ejecuta  Streamlit.
def main():
    #  Crea el panel lateral para los filtros.
    st.sidebar.title("🎬 Películas")
    
    # --------------------------------------
    # Genres, consulta 
    # --------------------------------------
    resp_genres = api("/data/genres")
    if resp_genres is None:
        resp_genres = []
    
    status = resp_genres.get("status", False)
    if status == False:
        st.error("Genres no disponible")
        return
    
    genre_data = json.loads(resp_genres.get("data", False))
    genre_columns = []
    for gen in genre_data:
        genre_columns.append(gen["genre"])
    
    # --------------------------------------
    # Objetos
    # --------------------------------------
    selected_genres = st.sidebar.multiselect(
        "Elige los Géneros:", options=sorted(genre_columns), default=[] 
    )
    rating_slider = st.sidebar.slider(
        "Filtro por Rating Promedio:", 0.0, 5.0, (0.0, 5.0) # tupla (min, max) para definir un rango
    )
    items_per_page = st.sidebar.selectbox(
        "Numero de Peliculas", ["10","15","20","25","30","50"]
    )
    
    # min_ratings_limit = int(df_procesado['rating_conteo'].quantile(0.75))
    # total_ratings_slider = st.sidebar.slider(
    #     "Filtro por Calificaciones:", 0, int(df_procesado['rating_conteo'].max()), min_ratings_limit
    # ) 

    # Agrega una sección para seleccionar el orden de los resultados.
    # st.sidebar.markdown("---")
    sort_by = st.sidebar.radio(
        "Elegir orden:",
        ["Rating", "Popularidad"],
        index=0 # Por defecto, ordena por Puntaje
    )
    parameters = {
        "order_by": sort_by,
        "genres": selected_genres,
        "rating_min": rating_slider[0],
        "rating_max": rating_slider[1],
        "items_per_page": items_per_page
    }
    
    # print(parameters)
    # --------------------------------------
    # Traer el listado de Movies con los filtros seleccionados 
    # --------------------------------------
    df = apiPost("/data/clean_movies", parameters)
    
    status = df.get("status", False)
    print(status)
    if status == False:
        st.error("La lista de peliculas está vacia")
        message = df.get("message", False)
        st.error(f"{message}")
        return

    df_filtrado = json.loads(df.get("data", False))
    st.dataframe(df_filtrado)
    
    
    
    # for d in df_filtrado:
    #     st.write(d["title"])
    # print(data)
    # col_categoricas = ['movieid', 'title', 'genres', 'rating_promedio', 'rating_conteo', 'tag', 'tmdbid']
    # df_procesado = pd.DataFrame(data, columns=col_categoricas)
    # df_procesado.reset_index(level=0, inplace=True)

    # genre_columns, year_columns = get_dynamic_columns(df_procesado)
    # print(genre_columns)
        

      
                
    #  Muestra las métricas principales (KPIs) en la parte superior.
    # st.header("Resultados del Filtro")
    # col1, col2 = st.columns(2)
    # col1.metric("Películas Encontradas", f"{len(df_filtrado):,}")
    # col2.metric("Total Películas en BD", f"{len(df_procesado):,}")
    # st.markdown("---")
    return 
        
        # # Crea las dos pestañas Pósteres y Análisis.
        # # tab_posters, tab_analisis = st.tabs(["🎬 Explorador de Peliculas", "📊 Análisis de Datos"])

        # #  Lógica de la Pestaña 1: Explorador de Pósteres.
        # # with tab_posters:
        # # st.subheader(f"Películas mas puntuadas en toda la historia  (por {sort_label})")
        # st.subheader(f"Películas mas puntuadas ")
        
        # if len(df_filtrado) == 0:
        #     st.warning("No se encontraron películas con los filtros seleccionados.")
        # else:
        #     # Muestra solo Top 20 para optimizar la carga.
        #     df_paginado = df_filtrado.head(20) 
        #     st.markdown(f"Mostrando el **Top 20** (ordenado por {sort_label}) de las **{len(df_filtrado)}** películas encontradas.")
            
        #     num_cols = 5
        #     cols = st.columns(num_cols)
        #     for i, row in enumerate(df_paginado.itertuples()):
        #         print(row.tmdbid)
        #         poster_url = get_poster_url(row["tmdbid"])
        #         with cols[i % num_cols]:
        #             st.image(poster_url, width='stretch', caption=f"{row.rating_promedio:.1f} ⭐ ({row.rating_conteo:,} votos)")
                    
        #             # Mantiene el título si es muy largo para mantener para q quede alineado el grid.
        #             title = row.title
        #             if len(title) > 30:
        #                 title = title[:30] + "..."
                    
        #             # Muestra el título ........
        #             st.markdown(f"**{title}**")
                    
        #             # Muestra el título  y  detalles.
        #             with st.expander("Más detalles"):
        #                 st.markdown(f"**Título:** {row.title}") # Título completo
        #                 st.write(f"**Géneros:** {row.genres.replace('|', ', ')}")
        #                 if pd.notna(row.tag):
        #                         st.write(f"**Tags:** {str(row.tag)[:100]}...")

if __name__ == "__main__":
    main()