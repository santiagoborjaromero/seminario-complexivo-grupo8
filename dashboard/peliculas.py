import streamlit as st
import pandas as pd
import os
import json
from dashboard.funciones import get_poster_url, api, apiPost

# Define las rutas a los archivos de datos procesados
BASE_DIR = os.getcwd() 
DEFAULT_POSTER = os.path.join(BASE_DIR, 'images', 'default.png')
LOGO = os.path.join(BASE_DIR, 'images', 'logom.png')

#  Función principal que ejecuta  Streamlit.
def main():
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
    movie_title = st.sidebar.text_input(
        "Búsqueda por titulo"
    )
    
    selected_genres = st.sidebar.multiselect(
        "Elige los Géneros:", options=sorted(genre_columns), default=[] 
    )
    rating_slider = st.sidebar.slider(
        "Rating: ⭐", 0.0, 5.0, (0.0, 5.0) # tupla (min, max) para definir un rango
    )
    count_slider = st.sidebar.slider(
        "Popularidad en votos:", 0.0, 68000.0, (30000.0, 68000.0) # tupla (min, max) para definir un rango
    )
    items_per_page = st.sidebar.selectbox(
        "Numero de Peliculas", ["10","15","20","25","30","50"]
    )
    
    # Agrega una sección para seleccionar el orden de los resultados.
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
        "items_per_page": items_per_page,
        "count_slider_min": count_slider[0],
        "count_slider_max": count_slider[1],
        "movie_title": movie_title
    }
    
    # print(parameters)
    # --------------------------------------
    # Traer el listado de Movies con los filtros seleccionados 
    # --------------------------------------
    # with st.spinner("Cargando películas ..."):
    #     time.sleep(2)
    df = apiPost("/data/clean_movies", parameters)
    status = df.get("status", False)
    if status == False:
        st.warning("La lista de películas está vacia")
        message = df.get("message", False)
        st.error(f"{message}")
        return

    df_filtrado = json.loads(df.get("data", False))

    col_categoricas = ['movieid', 'title', 'genres', 'rating_promedio', 'rating_conteo', 'tag', 'tmdbid']
    df_procesado = pd.DataFrame(df_filtrado, columns=col_categoricas)
    df_procesado.reset_index(level=0, inplace=True)
                
    if len(df_procesado) == 0:
        st.warning("No se encontraron películas con los filtros seleccionados.")
    else:
        col1,col2 = st.columns([0.25,4])
        with col1:
            st.image(LOGO, width=60)
        with col2:
            st.markdown("### Listado completo de Películas")
            
            
        num_cols = 5
        cols = st.columns(num_cols)
        for i, row in enumerate(df_procesado.itertuples()):
            poster_url = get_poster_url(row.tmdbid, DEFAULT_POSTER)
            with cols[i % num_cols]:
                st.image(poster_url, width='stretch', caption=f"{row.rating_promedio:.1f} ⭐ ({row.rating_conteo:,} votos)")
                
                # Mantiene el título si es muy largo para mantener para q quede alineado el grid.
                title = row.title
                if len(title) > 30:
                    title = title[:30] + "..."
                
                # Muestra el título ........
                # st.markdown(f"**{title}**")
                
                # Muestra el título  y  detalles.
                with st.expander("Más detalles"):
                    st.markdown(f"**Título:** {row.title}") # Título completo
                    st.write(f"**Géneros:** {row.genres.replace('|', ', ')}")
                    if pd.notna(row.tag):
                            st.write(f"**Tags:** {str(row.tag)[:100]}...")

if __name__ == "__main__":
    main()