import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os 

from dashboard.funciones import load_data, get_dynamic_columns, get_poster_url, api, apiPost

# Define la clave de la API de TMDB (v3 auth)
TMDB_API_KEY = "c8f4aca1c7dedc6184e0cf3f98e2665e"
# Define las rutas a los archivos de datos procesados
BASE_DIR = os.getcwd() 
DEFAULT_POSTER = os.path.join(BASE_DIR, 'images', 'default.png')
LOGO = os.path.join(BASE_DIR, 'images', 'logom.png')

def main():
    # --------------------------------------
    # Genres, consulta 
    # --------------------------------------
    resp_genres = api("/data/genres")
    
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
    selected_genres = st.sidebar.selectbox(
        "Géneros:", options=sorted(genre_columns)
    )
    items_per_page = st.sidebar.selectbox(
        "Numero de Peliculas", ["10","15","20","25","30","50"]
    )
    # # print(selected_genres)
    # --------------------------------------
    # Traer el listado de Movies recomendados por genero
    # --------------------------------------
    
    df = api(f"/recommendations/contenido/{selected_genres}/{items_per_page}")
    status = df.get("status", False)
    if status == False:
        st.warning("La lista de películas está vacia")
        message = df.get("message", False)
        st.error(f"{message}")
        return

    df_filtrado = json.loads(df.get("data", False))
    # st.dataframe(df_filtrado)

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
            st.markdown("### Películas Recomendadas por Género")
        
        num_cols = 5
        cols = st.columns(num_cols)
        for i, row in enumerate(df_procesado.itertuples()):
            poster_url = get_poster_url(row.tmdbid, DEFAULT_POSTER)
            with cols[i % num_cols]:
                st.image(poster_url, width='stretch', caption=f"{row.rating_promedio:.1f} ⭐ ({row.rating_conteo:,} votos)")
                # st.image(poster_url, width='stretch', caption=f"{row.rating_promedio:.1f} ⭐")
                
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