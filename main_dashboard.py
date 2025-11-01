import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="🔥 Recomendacion de Películas 🔥",
    page_icon="🔥", #https://docs.streamlit.io/develop/api-reference/navigation/st.page
    layout="wide"
)

st.title(" 🔥 Dashboard Recomendacíon Hibrida de Películas 🔥 ")


BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Define la ruta del archivo procesado
DATA_PROCESS_DIR = os.path.join(BASE_DIR, 'data', 'process')
PROCESSED_FILE = os.path.join(DATA_PROCESS_DIR, 'procesados_movies.csv')


@st.cache_data 
def load_data(file_path):
    """
    'load_data' carga el archivo CSV procesado del pipeline usando
     @st.cache_data para optimizar el rendimiento, para que Streamlit no lea el archivo en cada click.
    """
    try:
        df = pd.read_csv(file_path, encoding='latin1') 
        return df
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo 'procesados_movies.csv' en {file_path}")
        st.info("Por favor, ejecuta primero python main_pipeline.py para generar el archivo de datos procesados.")
        return None