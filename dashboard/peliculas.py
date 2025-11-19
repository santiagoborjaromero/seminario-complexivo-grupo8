import streamlit as st
import pandas as pd
import os
import json
from dashboard.funciones import get_poster_url, api, apiPost

# Define las rutas a los archivos de datos procesados
BASE_DIR = os.getcwd() 
DEFAULT_POSTER = os.path.join(BASE_DIR, 'images', 'default.png')
LOGO = os.path.join(BASE_DIR, 'images', 'logom.png')

current_user = st.session_state.user_data

if "logged_in" not in st.session_state or current_user == {}:
    st.session_state.logged_in = False
    st.session_state.user_data = {}

    
#  Función principal que ejecuta  Streamlit.
def main():
    
    userid = current_user["userid"]
    
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
    
    # Agrega una sección para seleccionar el orden de los resultados.
    
    filtro_general = st.sidebar.radio(
        "Elegir filtro de las peliculas:",
        [ "Tus calificadas", "Todas",],
        index=0 # Por defecto, ordena por Puntaje
    )
    
    movie_title = st.sidebar.text_input(
        "Búsqueda por titulo"
    )
    selected_genres = st.sidebar.multiselect(
        "Elige los Géneros:", options=sorted(genre_columns), default=[] 
    )
    rating_slider = st.sidebar.slider(
        "Rating: ⭐", 0.0, 5.0, (0.0, 5.0) # tupla (min, max) para definir un rango
    )
    
    rango = ( 0.0, 68000.0)
    index_orden = 0
    if filtro_general =="Todas":
        rango = ( 30000.0, 68000.0)
        index_orden = 0
        
    count_slider = st.sidebar.slider(
        "Popularidad en votos:", 0.0, 68000.0, rango # tupla (min, max) para definir un rango
    )
    # Agrega una sección para seleccionar el orden de los resultados.
    sort_by = st.sidebar.radio(
        "Elegir orden:",
        ["Rating", "Popularidad"],
        index=index_orden # Por defecto, ordena por Puntaje
    )
        
    items_per_page = st.sidebar.selectbox(
        "Numero de Peliculas", ["10","15","20","25","30","50"]
    )
    # --------------------------------------
    # Traer el listado de Movies con los filtros seleccionados 
    # --------------------------------------
    parameters = {
        "order_by": sort_by,
        "genres": selected_genres,
        "rating_min": rating_slider[0],
        "rating_max": rating_slider[1],
        "items_per_page": items_per_page,
        "count_slider_min": count_slider[0],
        "count_slider_max": count_slider[1],
        "movie_title": movie_title,
        "filter": filtro_general,
        "userid": userid
    }
    
    
    try:
        with st.spinner("Cargando películas ..."):
            df = apiPost("/data/clean_movies", parameters)
        status = df.get("status", False)
        if status == False:
            st.warning("La lista de películas está vacia")
            message = df.get("message", False)
            st.error(f"{message}")
            return
    except Exception as err:
        st.error(err)
        return

    df_filtrado = json.loads(df.get("data", False))
    if filtro_general =="Todas":
        col_categoricas = ['movieid', 'title', 'genres', 'rating_promedio', 'rating_conteo', 'tag', 'tmdbid']
    else:
        col_categoricas = ['movieid', 'title', 'genres', 'rating_usuario_promedio', 'rating_usuario_conteo', 'tag', 'tmdbid']
    df_procesado = pd.DataFrame(df_filtrado, columns=col_categoricas)
    df_procesado.reset_index(level=0, inplace=True)
                
    if len(df_procesado) == 0:
        st.warning("No se encontraron películas con los filtros seleccionados.")
    else:
        col1,col2 = st.columns([0.25,4])
        with col1:
            st.image(LOGO, width=60)
        with col2:
            if filtro_general =="Todas":
                st.markdown("### Listado completo de Películas")
            else:
                st.markdown("### Las Peliculas que mas alto calificaste")
            
            
        num_cols = 5
        cols = st.columns(num_cols)
        for i, row in enumerate(df_procesado.itertuples()):
            poster_url = get_poster_url(row.tmdbid, DEFAULT_POSTER)
            with cols[i % num_cols]:
                if filtro_general =="Todas":
                    st.image(poster_url, width='stretch', caption=f"{row.rating_promedio:.1f} ⭐ ({row.rating_conteo:,} votos)")
                else:
                    st.image(poster_url, width='stretch', caption=f"{row.rating_usuario_promedio:.1f} ⭐ ({row.rating_usuario_conteo:,} votos)")
                
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