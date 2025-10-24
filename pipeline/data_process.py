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
    rating_movies_promedio = rating.groupby("movieid")["rating"].mean()
    rating_movies_conteo = rating.groupby(["movieid"])["rating"].count()
    
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
    # Creo un campo indice y relleno con secuencial
    dim_rating["ratingid"] = range(1, len(dim_rating) + 1)
        
    return ratings_agg, dim_rating


def join_unique_tags(tags):
    return ', '.join(pd.unique(tags))

def procesar_tags(tags_df):
    """
    Realiza la limpieza  y agrupa los tags, ratings,  de las peliculas manejando los datos
    argumento tag_df,  como dataframe raw 
    retorna la data agrupada por el id de pelicula y tag
    """
    print("Procesando data")
    
    # Establecer campos en minusculas y sin espacios en blanco
    tags_df.columns = tags_df.columns.str.lower() # en minuscular
    tags_df.columns = tags_df.columns.str.strip() # quitar espacios en blanco
    
    # Eliminar tags NaN
    tags_df = tags_df.dropna(subset=["tag"], how="all")
    
    # Seleccionar data de tags que solo digitos
    data_numero = pd.to_numeric(tags_df['tag'], errors='coerce').notna()
    
    # Seleccionar todos lo que no sea numeros
    tags_df = tags_df[~data_numero]
    
    #Verificamos tod lo que no se str
    df_strings = tags_df[tags_df['tag'].apply(lambda x: isinstance(x, str))]
    
    # Reemplazamos valores que no son alfanumericos 
    df_strings['tag'] = df_strings['tag'].str.replace(r'[^a-zA-Z0-9]', '', regex=True)
    
    #Agrupacion de tags
    tags_agg = df_strings.groupby('movieid')['tag'].apply(join_unique_tags)

    return tags_agg
