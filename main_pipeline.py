import pandas as pd
import numpy as np
from pipeline.data_loader import cargar_datos
from pipeline.data_process import procesar_ratings, procesar_movie, procesar_tags, procesar_link
from pipeline.data_saving import guardar_informacion
import sys

if __name__ == "__main__":
    # --------------------------------------
    # Lista de archivo (con link.csv)
    # --------------------------------------
    files = ["movie.csv", "tag.csv",  "link.csv", "rating.csv"]
    # files = ["movie.csv", "tag.csv",  "link.csv"]

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
    print(type(df_movie))
    
    # Procesando Tags
    df_tags_general, tags = procesar_tags(dict_df[files[1]])
    print(type(df_tags_general))
    
    # Procesando links
    df_links = procesar_link(dict_df[files[2]])
    print(type(df_links))
    
    # Procesando Rating
    df_rating_general, dim_rating , rating_source = procesar_ratings(dict_df[files[3]])
    print(type(df_rating_general))

    # --------------------------------------
    # Uniones
    # --------------------------------------
    print("-----------------------------------")
    print("Merge - Iniciando fusiones entre tablas...")
    print("Merge - Movie + Rating")
    tabla_hecho_parcial = pd.merge(df_movie, df_rating_general, on="movieid", how="left")
    print("Merge - Movie + Rating + Tags")
    tabla_hecho_parcial_2 = pd.merge(tabla_hecho_parcial, df_tags_general, on="movieid", how="left")
    print("Merge - Movie + Rating + Tags + Links")
    tabla_hecho = pd.merge(tabla_hecho_parcial_2, df_links, left_on="movieid", right_on="movieid", how="left")
    
    # Limpia columna duplicada de movieid que viene de df_links
    if 'movieid' in tabla_hecho.columns:
        tabla_hecho = tabla_hecho.drop(columns=['movieid'])
    
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