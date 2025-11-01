# main_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="🔥 Recomendacion de Películas 🔥",
    page_icon="🔥",
    layout="wide"
)

st.title(" 🔥 Dashboard Recomendacíon Hibrida de Películas 🔥 ")

# --- Definición de Rutas ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Define la ruta del archivo procesado
DATA_PROCESS_DIR = os.path.join(BASE_DIR, 'data', 'process')
PROCESSED_FILE = os.path.join(DATA_PROCESS_DIR, 'procesados_movies.csv')

# --- Funciones de Carga  ---

@st.cache_data 
def load_data(file_path):
    """
    'load_data' carga el archivo CSV procesado del pipeline usando
     @st.cache_data para optimizar el rendimiento.
    """
    try:
        df = pd.read_csv(file_path, encoding='latin1') 
        return df
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo 'procesados_movies.csv' en {file_path}")
        st.info("Por favor, ejecuta primero python main_pipeline.py para generar el archivo de datos procesados.")
        return None

@st.cache_data
def get_dynamic_columns(df):
    """
    La función 'get_dynamic_columns' inspecciona el df y
    extrae las columnas de género y las de año desde (Pivot).
    """
    base_cols = ['movieid', 'title', 'genres', 'rating_promedio', 'rating_conteo', 'tags_agrupados']
    year_cols = [col for col in df.columns if col.isdigit() and len(col) == 4]
    genre_cols = [col for col in df.columns if col not in base_cols and col not in year_cols]
    
    return genre_cols, year_cols

# --- Función Principal ---
def main():
    """
    Función principal ejecuta Streamlit.
    """
    st.markdown("Versión V1.0: Visualizando los datos de `procesados_movies.csv`.")

    # Carga los datos 
    df_procesado = load_data(PROCESSED_FILE)
    
    if df_procesado is None:
        return
  
    # Llama a la función helper para obtener las listas de columnas
    genre_columns, year_columns = get_dynamic_columns(df_procesado)

    #  Barra Lateral  ---
    st.sidebar.header("Filtros Interactivos")

    # Crea un widget géneros
    selected_genres = st.sidebar.multiselect(
        "Seleccionar Géneros (Lógica 'Y'):",
        options=sorted(genre_columns), # Usa de género dinámicamente
        default=[] 
    )

    # Crea un widget  rango de rating
    rating_slider = st.sidebar.slider(
        "Filtrar por Rating Promedio:",
        min_value=0.0,
        max_value=5.0,
        value=(0.0, 5.0) # tupla (min, max) para definir un rango
    )

    # Crea un slider para la popularidad basado en 'rating_conteo'
    min_ratings_limit = int(df_procesado['rating_conteo'].quantile(0.75))
    total_ratings_slider = st.sidebar.slider(
        "Filtrar por Mínimo de Calificaciones:",
        min_value=0,
        max_value=int(df_procesado['rating_conteo'].max()),
        value=min_ratings_limit
    ) 


if __name__ == "__main__":
    main()