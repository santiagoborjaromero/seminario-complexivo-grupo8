import pandas as pd

def procesar_movie(movie):
    # Establecer campos en minusculas y sin espacios en blanco
    movie.columns = movie.columns.str.lower() # en minuscular
    movie.columns = movie.columns.str.strip() # quitar espacios en blanco
    return movie
    

def procesar_ratings(rating):
    # Establecer campos en minusculas y sin espacios en blanco
    rating.columns = rating.columns.str.lower() # en minuscular
    rating.columns = rating.columns.str.strip() # quitar espacios en blanco
    
    # Cambio de timestamp tipo object a datetime
    rating["timestamp"] = pd.to_datetime(rating["timestamp"])
    # Creacion de dos columnas year y month 
    rating["year"] =  rating['timestamp'].dt.year
    rating["month"] =  rating['timestamp'].dt.month
    
    # Agrupacion general por pelicula 
    rating_movies_promedio = rating.groupby("movieid")["rating"].mean().reset_index("movieid")
    rating_movies_conteo = rating.groupby(["movieid"])["rating"].count().reset_index("movieid")
    
    # Union de promedio y conteo para que sea unido a movies de forma general
    ratings_agg = pd.merge(rating_movies_promedio, rating_movies_conteo, on="movieid", how="left")
    
    # Cambio de nombre de columnas
    ratings_agg = ratings_agg.rename(
        columns={
            "rating_x": "rating_promedio",
            "rating_y": "rating_conteo"
        }
    )
    
    # Creacion de la tablas de dimension 
    # Agrupacion
    grupo = rating.groupby(["movieid","userid", "year","month"])["rating"]
    rating_movies_year_month_promedio = grupo.mean().reset_index()
    rating_movies_year_month_conteo = grupo.count().reset_index()
    # Union
    dim_rating = pd.merge(rating_movies_year_month_promedio, rating_movies_year_month_conteo, on=["movieid","userid", "year","month"], how="left")
    # Cambio de nombre de columnas
    dim_rating = dim_rating.rename(
        columns={
            "rating_x": "promedio",
            "rating_y": "conteo"
        }
    )
        
    return ratings_agg, dim_rating


def procesar_tags(tags_df):
    """
    Realiza la limpieza  y agrupa los tags, ratings,  de las peliculas manejando los datos
    argumento tag_df,  como dataframe raw 
    retorna la data agrupada por el id de pelicula y tag
    """
    print("Procesando data")
    tags_agg =tags_df.groupby("movieId")["tag"].apply(
        lambda x: ' '.join(str(tag) for tag in x if pd.notna(tag))
        ).reset_index()
    
    tags_agg = tags_agg.rename(columns={"tag": "tags_agrupados"})
    print (" Tags Agrupados y Limpios ")
    return tags_agg

