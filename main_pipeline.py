import pandas as pd
import numpy as np
from pipeline.data_loader import cargar_datos
from pipeline.data_process import procesar_ratings, procesar_movie, procesar_tags
from pipeline.data_saving import guardar_informacion
import sys

if __name__ == "__main__":
    # --------------------------------------
    # Lista de archivo
    # --------------------------------------
    files = ["movie.csv", "tag.csv", "rating.csv"]

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
    df_movie, movie_source, unique_genres = procesar_movie(dict_df[files[0]])
    # print(df_movie.head())

    # Procesando Rating
    df_rating_general, dim_rating , rating_source= procesar_ratings(dict_df[files[2]])
    # Procesando Tags
    df_tags_general, tags = procesar_tags(dict_df[files[1]])
    
    # --------------------------------------
    # Uniones
    # --------------------------------------
    tabla_hecho_parcial = pd.merge(df_movie, df_rating_general, on="movieid", how="left")
    tabla_hecho = pd.merge(tabla_hecho_parcial, df_tags_general, on="movieid", how="left")
    
    # --------------------------------------
    # Originales Limpios
    # --------------------------------------
    
    archivos = [
        # {"file_name": "movie_proc", "target": df_movie},
        {"file_name": "movie", "target": movie_source},
        {"file_name": "rating", "target": rating_source},
        {"file_name": "tag", "target": tags},
        {"file_name": "genres", "target": unique_genres},
        {"file_name": "procesados_movies", "target": tabla_hecho},
        {"file_name": "procesados_ratings", "target": dim_rating},
    ]
    
    for file in archivos:
        print(f"Guardando {file["file_name"]}")
        file["target"].head()
        guardar_informacion(f"{file['file_name']}.csv",file["target"])
    
    