# scripts/load_data.py

import pandas as pd
import os
from typing import Dict, Any

# --- CONSTRUCCIÓN DE RUTA ABSOLUTA ---    
# Obtiene la ruta de la carpeta 'scripts'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# RUTA DE LA CARPETA DE DATOS (sube un nivel '..' y entra a 'data')
DATA_FOLDER_PATH = os.path.join(SCRIPT_DIR, "..", "data")

def cargar_datos(filename: str) -> pd.DataFrame or None:
    """Carga un archivo CSV específico y maneja errores."""
    # Construye la ruta completa: .../moviematch/data/filename
    full_path = os.path.join(DATA_FOLDER_PATH, filename)
    
    print(f"Cargando datos: {filename} desde {full_path}")
    try:
        df = pd.read_csv(full_path)
        print(f"Datos '{filename}' cargados. Filas: {len(df)}")
        return df
    except FileNotFoundError:
        print(f"ERROR: Archivo {filename} no encontrado en la ruta {full_path}")
        return None
    except Exception as err:
        print(f"ERROR inesperado al cargar {filename}: {err}")
        return None

# --- FUNCIÓN DE PRUEBA (SOLO SE EJECUTA AL LLAMAR AL ARCHIVO DIRECTAMENTE) ---    
if __name__ == "__main__":
    
    print(f"Ejecutando script desde : {os.path.abspath(__file__)}")
    
    # Llamar a la función para cargar los dos CSVs principales
    df_movies = cargar_datos("movie.csv")
    df_ratings = cargar_datos("rating.csv")
    
    if df_movies is not None:
        print("\n--- Vista de Películas ---")
        print(df_movies.head())  
        print("--- Info del DataFrame de Películas ---")
        df_movies.info(show_counts=True)
    
    if df_ratings is not None:
        print("\n--- Vista de Calificaciones ---")
        print(df_ratings.head())
        print("--- Info del DataFrame de Calificaciones ---")
        df_ratings.info(show_counts=True)