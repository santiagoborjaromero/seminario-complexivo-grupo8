import pandas as pd
import numpy as np
from pipeline.data_loader import cargar_datos
from pipeline.dama_movie_process import clean_and_kpis_movies
from pipeline.dama_rating_process import clean_and_kpis_ratings 
from pipeline.dama_tag_process import clean_and_kpis_tags
from pipeline.data_saving import guardar_informacion
import sys

if __name__ == "__main__":
    # --------------------------------------
    # Lista de archivo (con link.csv)
    # --------------------------------------
    files = ["movie.csv", "tag.csv", "rating.csv"]
    # files = ["movie.csv", "tag.csv",  "rating.csv"]

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
    # Limpia y crea  KPIs de Movies
    # --------------------------------------
    clean_movie, kpis_movie = clean_and_kpis_movies(dict_df[files[0]])    # Limpia y   calcula KPIs
    print(kpis_movie)
    
    # --------------------------------------
    # Carga las columnas de movies Id para validación cruzada
    # --------------------------------------
    movies_ids = None                   # Inicializa catálogo
    movies = dict_df[files[0]]    # Carga movies
    mcols = {c.lower(): c for c in movies.columns}  # Mapa de columnas
    movieId_col = mcols.get("movieid", "movieId" if "movieId" in movies.columns else movies.columns[0]) # Detecta columna
    movies_ids = movies[movieId_col]             # Serie con IDs

    # --------------------------------------
    # Limpia y crea  KPIs de Tags
    # --------------------------------------
    clean_tag, kpis_tag = clean_and_kpis_tags(dict_df[files[1]],movies_ids)    # Limpia y   calcula KPIs
    print(kpis_tag)
    
    # --------------------------------------
    # Limpia y crea  KPIs de Ratings
    # --------------------------------------
    clean_rating, kpis_rating = clean_and_kpis_ratings(dict_df[files[2]],movies_ids)    # Limpia y   calcula KPIs
    print(kpis_rating)
    
    # --------------------------------------
    #  Guarda los arhivos  KPIs y limpios
    # --------------------------------------
    archivos = [
        # {"file_name": "movie", "target": movie_source},
        {"file_name": "movie_kpis", "target": kpis_movie},
        {"file_name": "tag_kpis", "target": kpis_tag},
        {"file_name": "rating_kpis", "target": kpis_rating},
        #{"file_name": "genres", "target": unique_genres},
        #{"file_name": "movie_perfil_contenido", "target": perfil_contenido},
        # {"file_name": "procesados_ratings", "target": dim_rating},
    ]
    
    for file in archivos:
        print(f"Guardando {file['file_name']}")
        guardar_informacion(f"{file['file_name']}.csv", file["target"])
    
   
    