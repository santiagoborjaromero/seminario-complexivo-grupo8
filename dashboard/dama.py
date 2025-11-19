import streamlit as st
import pandas as pd
import plotly.express as px
import os
import requests
import json

from dashboard.funciones import load_data, get_dynamic_columns, get_poster_url, api

# Configura los metadatos de la página (título, ícono, layout)
# st.set_page_config(
#     page_title="🔥 Calidad de Datos 🔥",
#     page_icon="🎬",#https://docs.streamlit.io/develop/api-reference/navigation/st.page
#     layout="wide"
# )

# Define las rutas a los archivos de datos procesados
BASE_DIR = os.getcwd() 
# PROCESSED_FILE = os.path.join(BASE_DIR, 'data', 'process', 'procesados_movies.csv')
DEFAULT_POSTER = os.path.join(BASE_DIR, 'images', 'default.png')

#  Función principal que ejecuta  Streamlit.
def main():
    #  Crea el panel lateral para los filtros.
    st.sidebar.title("DAMA")
    
    #Carga  el catalogo de KPI's de Dama
    resp_dama = api("/data/catalog_dama")
    if resp_dama is None:
        resp_dama = []
    
    status = resp_dama.get("status", False)
    if status == False:
        st.error("KPI's no disponible")
        return
    
    dama_data = json.loads(resp_dama.get("data", False))
    dama_columns = []
    for dama in dama_data:
        dama_columns.append(dama["dama"])
    
    # Selección de KPI's de Dama    
    selected_dama = st.sidebar.selectbox(
        "Elige el KPI:",
        # options=["-- Selecciona --"] + sorted(dama_columns)
        options=sorted(dama_columns)
    )
    
    if selected_dama == "Movie":
        #Carga la data de movie_kpis
        resp_movie_dama = api("/data/movie_dama")
        if resp_movie_dama is None:
            resp_movie_dama = []
        status = resp_movie_dama.get("status", False)
        if status == False:
            st.error("Movie KPI's no disponible")
            return
        movie_dama_data = json.loads(resp_movie_dama.get("data", False))
        df_movie_dama = pd.DataFrame(movie_dama_data)
        st.dataframe(df_movie_dama.head(15))
        st.image('images/movie_dama.png', caption='Movie Dama KPI', width='stretch')
    elif selected_dama == "Rating":
        #Carga la data de rating_kpis
        resp_rating_dama = api("/data/rating_dama")
        if resp_rating_dama is None:
            resp_rating_dama = []
        status = resp_rating_dama.get("status", False)
        if status == False:
            st.error("Rating KPI's no disponible")
            return
        rating_dama_data = json.loads(resp_rating_dama.get("data", False))
        df_rating_dama = pd.DataFrame(rating_dama_data)
        st.dataframe(df_rating_dama.head(15))
        st.image('images/rating_dama.png', caption='Movie Dama KPI', width='stretch')
    elif selected_dama == "Tag":
        #Carga la data de tag_kpis
        resp_tag_dama = api("/data/tag_dama")
        if resp_tag_dama is None:
            resp_tag_dama = []
        status = resp_tag_dama.get("status", False)
        if status == False:
            st.error("Tag KPI's no disponible")
            return
        tag_dama_data = json.loads(resp_tag_dama.get("data", False))
        df_tag_dama = pd.DataFrame(tag_dama_data)
        st.dataframe(df_tag_dama.head(15))
        st.image('images/tag_dama.png', caption='Movie Dama KPI', width='stretch')
    
    
if __name__ == "__main__":
    main()