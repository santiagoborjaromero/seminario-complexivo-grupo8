# main_pipeline.py
import pandas as pd
import numpy as np
from pipeline.data_loader import cargar_datos
from pipeline.data_process import procesar_ratings, procesar_movie, procesar_tags
from pipeline.data_saving import guardar_informacion
import sys

if __name__ == "__main__":
    # --------------------------------------
    # Lista de archivo (¡AÑADIMOS LINK.CSV!)
    # --------------------------------------
    files = ["movie.csv", "tag.csv", "rating.csv", "link.csv"] # <-- ¡NUEVO!

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
    # Procesando Rating
    df_rating_general, dim_rating , rating_source = procesar_ratings(dict_df["rating.csv"])
    # Procesando Tags
    df_tags_general = procesar_tags(dict_df["tag.csv"])
    
    # Cargo y limpio links
    print("-----------------------------------")
    print("Procesando Data Link")
    df_links = dict_df["link.csv"]
    # Limpiar links: solo queremos las columnas clave y eliminar nulos
    df_links = df_links[['movieId', 'tmdbId']].dropna()
    df_links['tmdbId'] = df_links['tmdbId'].astype(int)

    
    # AÑADO LINKS
    
    print("-----------------------------------")
    print("Iniciando fusiones (merge) de tablas...")
    tabla_hecho_parcial = pd.merge(df_movie, df_rating_general, on="movieid", how="left")
    tabla_hecho_parcial_2 = pd.merge(tabla_hecho_parcial, df_tags_general, on="movieid", how="left")
    
    tabla_hecho = pd.merge(tabla_hecho_parcial_2, df_links, left_on="movieid", right_on="movieId", how="left")
    
    if 'movieId' in tabla_hecho.columns:
        tabla_hecho = tabla_hecho.drop(columns=['movieId'])
    
    # --------------------------------------
    # Originales Limpios
    # --------------------------------------
    
    archivos = [
        {"file_name": "movie", "target": movie_source},
        {"file_name": "rating", "target": rating_source},
        {"file_name": "tag", "target": df_tags_general},
        {"file_name": "procesados_movies", "target": tabla_hecho},
        {"file_name": "procesados_ratings", "target": dim_rating},
    ]
    
    for file in archivos:
        print(f"Guardando {file['file_name']}")
        # file["target"].head() # Comentado para evitar prints largos
        guardar_informacion(f"{file['file_name']}.csv", file["target"])