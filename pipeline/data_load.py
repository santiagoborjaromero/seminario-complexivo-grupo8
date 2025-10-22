import pandas as pd
import os

def cargar_datos(data_dir):
    """ 
    Carga los archivos movie, rating, tag
    argumento: data_dir como string a la ruta data\
    retorna una tupla de los dataframes de los archivos cargados con none si existe fallos
    """
    try:
        MOVIE_FILE =os.path.join(data_dir, "movie.csv")
        RATING_FILE=os.path.join(data_dir, "rating.csv")
        TAG_FILE=os.path.join(data_dir, "tag.csv")

        movies_df= pd.read_csv(MOVIE_FILE)
        ratings_df=pd.read_csv(RATING_FILE)
        tags_df=pd.read_csv("tag.csv")

        print("Archivos cargados Exitosamente")
        return movies_df, ratings_df, tags_df
    
    except FileNotFoundError as e:
        print(f"No se encontro el Aerchivo en {e.filename}.")
        return None,None,None