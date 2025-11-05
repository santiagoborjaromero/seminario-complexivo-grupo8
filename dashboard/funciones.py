import streamlit as st
import pandas as pd
import plotly.express as px
import os
import requests
import math 
#---------------------------------------------------------
# Define las rutas a los archivos de datos procesados
#---------------------------------------------------------

BASE_DIR = os.getcwd() 
DATA_PROCESS_DIR = os.path.join(BASE_DIR, 'data', 'process')

@st.cache_data
def load_data(file_path):
    PROCESSED_FILE = os.path.join(DATA_PROCESS_DIR, file_path)
    """
    Carga el archivo CSV procesado
    Usa @st.cache_data para optimizar el rendimiento y evitar recargas.
    """
    try:
        df = pd.read_csv(PROCESSED_FILE, encoding='latin1')
        return df
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo {PROCESSED_FILE}")
        st.info("Por favor, ejecuta primero el pipeline .")
        return None

@st.cache_data
def get_dynamic_columns(df):
    """
    Extrae las columnas de género (One-Hot) 
    y las de año (Pivot) del DataFrame.
    """
    # Define las columnas base que no son ni géneros ni años.
    base_cols = ['movieid', 'title', 'genres', 'rating_promedio', 'rating_conteo', 'tag', 'tmdbid']
    # Identifica las columnas de año (numéricas de 4 dígitos).
    year_cols = [col for col in df.columns if col.isdigit() and len(col) == 4]
    # Identifica las columnas de género (las restantes).
    genre_cols = [col for col in df.columns if col not in base_cols and col not in year_cols]
    return genre_cols, year_cols