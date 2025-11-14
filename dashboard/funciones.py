import streamlit as st
import pandas as pd
import os
import requests
#---------------------------------------------------------
# Define las rutas a los archivos de datos procesados
#---------------------------------------------------------

# API_BASE_URL = "https://api-seminario-complexivo-grupo8.onrender.com"
API_BASE_URL = "http://localhost:8000"
BASE_DIR = os.getcwd() 
DATA_PROCESS_DIR = os.path.join(BASE_DIR, 'data', 'process')
TMDB_API_KEY = "c8f4aca1c7dedc6184e0cf3f98e2665e"


@st.cache_data
def load_data(file_path):
    PROCESSED_FILE = os.path.join(DATA_PROCESS_DIR, file_path)
    """
    Carga el archivo CSV procesado
    Usa @st.cache_data para optimizar el rendimiento y evitar recargas.
    """
    try:
        df = pd.read_csv(PROCESSED_FILE, encoding='utf8')
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
    # Se añade 'release_year' 
    base_cols = ['movieid', 'title', 'genres', 'rating_promedio', 'rating_conteo', 'tag', 'tmdbid', 'release_year']
    
    # Identifica las columnas de año (numéricas de 4 dígitos).
    year_cols = [col for col in df.columns if col.isdigit() and len(col) == 4]
    # Identifica las columnas de género (las restantes).
    genre_cols = [col for col in df.columns if col not in base_cols and col not in year_cols]
    return genre_cols, year_cols


def get_poster_url(tmdb_id, DEFAULT_POSTER):
    # Si el tmdbid es nulo (NaN), devuelve el póster por defecto.
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
    
    
def api(url_path,data={}):
    try:
        response = requests.get(f"{API_BASE_URL}{url_path}", json=data, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error al cargar filtros desde la API: {e}"
    
def apiPost(url_path, data):
    try:
        response = requests.post(f"{API_BASE_URL}{url_path}", json=data, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error al cargar filtros desde la API: {e}"