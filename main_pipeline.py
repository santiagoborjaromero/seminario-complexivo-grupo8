import pandas as pd
import numpy as np
from pipeline.data_loader import cargar_datos
from pipeline.data_process import procesar_ratings, procesar_movie, procesar_tags
from pipeline.func import guardar_informacion
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
    df_movie = procesar_movie(dict_df[files[0]])
    # Procesando Rating
    df_rating_general, dim_rating = procesar_ratings(dict_df[files[2]])
    # Procesando Tags
    df_tags_general = procesar_tags(dict_df[files[1]])
    
    # --------------------------------------
    # Uniones
    # --------------------------------------
    tabla_hecho_parcial = pd.merge(df_movie, df_rating_general, on="movieid", how="left")
    tabla_hecho = pd.merge(tabla_hecho_parcial, df_tags_general, on="movieid", how="left")
    
    # --------------------------------------
    # Resultados
    # --------------------------------------
    print("TABLA DE HECHO `h_movie`")
    print(tabla_hecho.head())
    guardar_informacion("new_h_movie.csv", tabla_hecho)
    
    
    print("TABLA DIMENSION `d_rating`")
    print(dim_rating.head())
    guardar_informacion("new_d_rating.csv",dim_rating)

    
    
    
    
    
    


