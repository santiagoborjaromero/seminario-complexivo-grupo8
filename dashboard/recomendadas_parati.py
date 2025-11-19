import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

from dashboard.funciones import load_data, get_dynamic_columns, get_poster_url, api, apiPost

# Define la clave de la API de TMDB (v3 auth)
TMDB_API_KEY = "c8f4aca1c7dedc6184e0cf3f98e2665e"

st.session_state.liked_movie_title = ""

BASE_DIR = os.getcwd() 

M = os.path.join(BASE_DIR, 'images', 'M.png')
F = os.path.join(BASE_DIR, 'images', 'F.png')
LOGO = os.path.join(BASE_DIR, 'images', 'logom.png')
current_user = st.session_state.user_data

if "logged_in" not in st.session_state or current_user == {}:
    st.session_state.logged_in = False
    st.session_state.user_data = {}

if (current_user["genero"] == "M"):
    st.sidebar.image(M,f"{current_user["nombre"]}")
else:
    st.sidebar.image(F,f"{current_user["nombre"]}")

st.sidebar.caption(f"Rating Votado {current_user["rating"]:.1f} ⭐ ({current_user["votos"]:,} votos)")
st.sidebar.caption(f":material/mail: {current_user["email"]}")
st.sidebar.caption(f":material/explore_nearby: {current_user["provincia"]}")

items_per_page = st.sidebar.selectbox(
    "Numero de Peliculas", ["10","15","20","25","30","50"]
)
method_abr = st.sidebar.selectbox(
    "Método de Recomendacion", ["KNN","SVD"]
)

if method_abr == "KNN":
    method = "colaborativa"
else:
    method = "svd"
    

# Define las rutas a los archivos de datos procesados
BASE_DIR = os.getcwd() 
DEFAULT_POSTER = os.path.join(BASE_DIR, 'images', 'default.png')
API_BASE_URL = "http://localhost:8000"


def main():
    col1,col2 = st.columns([0.25,4])
    with col1:
        st.image(LOGO, width=60)
    with col2:
        st.markdown("### Películas Recomendadas para ti")

    # --------------------------------------
    # Traer el listado de Movies con prediccion
    # --------------------------------------
    with st.spinner("Cargando recomendaciones..."):
        df = api(f"/recommendations/{method}/{current_user["userid"]}/{items_per_page}")
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
        num_cols = 5
        cols = st.columns(num_cols)
        primera_pelicula = ""
        nombre_de_peliculas = []
    
        for i, row in enumerate(df_procesado.itertuples()):
            poster_url = get_poster_url(row.tmdbid, DEFAULT_POSTER)
            with cols[i % num_cols]:
                
                with st.container(border=True):
                    st.image(poster_url, width='stretch', caption=f"{row.rating_promedio:.1f} ⭐ ({row.rating_conteo:,} votos)")
                    
                    # Mantiene el título si es muy largo para mantener para q quede alineado el grid.
                    title = row.title
                    
                    nombre_de_peliculas.append(title)
                    
                    if len(title) > 30:
                        title = title[:30] + "..."
                    
                    # Muestra el título ........
                    # st.markdown(f"**{title}**")
                    
                    if st.button(key=f"Peli{row.movieid}", label="", icon=":material/thumb_up:"):
                        # Guardar en session_state qué película fue likeada
                        st.session_state.liked_movie_title = title
                        # st.query_params.movie_title = title
                        # st.switch_page(f"pages/porquetegusto.py")
                        
                    # Muestra el título  y  detalles.
                    with st.expander("Más detalles"):
                        st.markdown(f"**Título:** {row.title}") # Título completo
                        st.write(f"**Géneros:** {row.genres.replace('|', ', ')}")
                        if pd.notna(row.tag):
                            st.write(f"**Tags:** {str(row.tag)[:100]}...")
        if ("liked_movie_title" in st.session_state) & (st.session_state.liked_movie_title != "") :
            col1,col2 = st.columns([0.25,4])
            with col1:
                st.image(LOGO, width=60)
            with col2:
                st.subheader(f"Porque te gustó {st.session_state.liked_movie_title}")
            
            # -----------------------------------------------------
            # Traer el listado de Movies con prediccion por nombre
            # -----------------------------------------------------
            with st.spinner("Cargando recomendaciones..."):
                df2 = api(f"/recommendations/pelicula/{st.session_state.liked_movie_title}")
                
            status = df2.get("status", False)
            if status == False:
                st.warning("La lista de películas está vacia")
                message = df2.get("message", False)
                st.error(f"{message}")
                return
            
            df2_filtrado = json.loads(df2.get("data", False))

            col_categoricas = ['movieid', 'title', 'genres', 'rating_promedio', 'rating_conteo', 'tag', 'tmdbid']
            df2_procesado = pd.DataFrame(df2_filtrado, columns=col_categoricas)
            df2_procesado.reset_index(level=0, inplace=True)
            num_cols = 5
            cols = st.columns(num_cols)
            
            for i, row in enumerate(df2_procesado.itertuples()):
                if i==0:
                    continue
                poster_url = get_poster_url(row.tmdbid, DEFAULT_POSTER)
                with cols[i % num_cols]:
                    
                    st.image(poster_url, width='stretch', caption=f"{row.rating_promedio:.1f} ⭐ ({row.rating_conteo:,} votos)")
                    
                    # Mantiene el título si es muy largo para mantener para q quede alineado el grid.
                    title = row.title
                    # Muestra el título  y  detalles.
                    with st.expander("Más detalles"):
                        st.markdown(f"**Título:** {row.title}") # Título completo
                        st.write(f"**Géneros:** {row.genres.replace('|', ', ')}")
                        if pd.notna(row.tag):
                                st.write(f"**Tags:** {str(row.tag)[:100]}...")
            
            
    
    
if __name__ == "__main__":
    main()