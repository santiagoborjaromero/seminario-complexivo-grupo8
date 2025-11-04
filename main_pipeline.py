import pandas as pd
import numpy as np
from pipeline.data_loader import cargar_datos
from pipeline.data_process import procesar_ratings, procesar_movie, procesar_tags
from pipeline.data_saving import guardar_informacion
import sys

if __name__ == "__main__":
    # --------------------------------------
    # Lista de archivo (con link.csv)
    # --------------------------------------
    files = ["movie.csv", "tag.csv", "rating.csv", "link.csv"]

    # --------------------------------------
    # Carga de datos CSV
    # --------------------------------------
    dict_df = cargar_datos(files)
    
    # --------------------------------------
    # Evaluacion si hay data prosigue
    # --------------------------------------
    if dict_df is None:
        sys.exit(0) 
    
    # --------------------------------------
    # Procesamiento de la informacion
    # --------------------------------------
    
    # Procesando Movies
    df_movie, movie_source = procesar_movie(dict_df["movie.csv"])
    
    # --- ¡CORRECCIÓN 1! ---
    # Forzar que 'movieid' sea numérico y luego entero
    print("-----------------------------------")
    print("Limpiando IDs de df_movie...")
    df_movie['movieid'] = pd.to_numeric(df_movie['movieid'], errors='coerce')
    df_movie = df_movie.dropna(subset=['movieid']) # Eliminar películas con ID malo
    df_movie['movieid'] = df_movie['movieid'].astype(int)

    # Procesando Rating
    df_rating_general, dim_rating , rating_source = procesar_ratings(dict_df["rating.csv"])
    # Procesando Tags
    df_tags_general = procesar_tags(dict_df["tag.csv"])
    
    
    # Limpiar y forzar tipos en df_links
    print("-----------------------------------")
    print("Procesando Data Link")
    df_links = dict_df["link.csv"]
    df_links = df_links[['movieId', 'tmdbId']].dropna()
    # cambio a que 'movieId' y 'tmdbId' sean numéricos y luego enteros
    df_links['movieId'] = pd.to_numeric(df_links['movieId'], errors='coerce')
    df_links['tmdbId'] = pd.to_numeric(df_links['tmdbId'], errors='coerce')
    df_links = df_links.dropna(subset=['movieId', 'tmdbId'])
    df_links['movieId'] = df_links['movieId'].astype(int)
    df_links['tmdbId'] = df_links['tmdbId'].astype(int)

    # --------------------------------------
    # Uniones
    # --------------------------------------
    print("-----------------------------------")
    print("Iniciando fusiones (merge) de tablas...")
    tabla_hecho_parcial = pd.merge(df_movie, df_rating_general, on="movieid", how="left")
    tabla_hecho_parcial_2 = pd.merge(tabla_hecho_parcial, df_tags_general, on="movieid", how="left")
    
    #  merge  de 'movieid' (int) + 'movieId' (int)
    tabla_hecho = pd.merge(tabla_hecho_parcial_2, df_links, left_on="movieid", right_on="movieId", how="left")
    
    # Limpia columna duplicada de movieId que viene de df_links
    if 'movieId' in tabla_hecho.columns:
        tabla_hecho = tabla_hecho.drop(columns=['movieId'])
    
    # --------------------------------------
    # Guardado de Archivos
    # --------------------------------------
    
    archivos = [
        {"file_name": "movie", "target": movie_source},
        {"file_name": "rating", "target": rating_source},
        {"file_name": "tag", "target": tags},
        {"file_name": "genres", "target": unique_genres},
        {"file_name": "procesados_movies", "target": tabla_hecho},
        {"file_name": "procesados_ratings", "target": dim_rating},
    ]
    
    for file in archivos:
        print(f"Guardando {file['file_name']}")
        guardar_informacion(f"{file['file_name']}.csv", file["target"])