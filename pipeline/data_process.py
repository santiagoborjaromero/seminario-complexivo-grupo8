import pandas as pd

def procesar_movie(movie):
    print("-----------------------------------")
    print("Procesando Data Movie")
    print("Procesando Data Movie - Conversión de campos en minusculas y espacios en blanco")
    # Establecer campos en minusculas y sin espacios en blanco
    movie.columns = movie.columns.str.lower() # en minuscular
    movie.columns = movie.columns.str.strip() # quitar espacios en blanco

    print("Procesando Data Movie - Aplicando One-Hot Encoding a la columna 'genres'")
    # Separar generos por '|' y crear columnas dummy (One-Hot Encoding)
    genres_dummies = movie['genres'].str.get_dummies('|')
    
    # Unir las nuevas columnas de generos al dataframe original
    movie = pd.concat([movie, genres_dummies], axis=1)

    return movie
    

def procesar_ratings(rating):
    print("-----------------------------------")
    print("Procesando Data Rating")
    print("Procesando Data Rating - Conversión de campos en minusculas y espacios en blanco")
    # Establecer campos en minusculas y sin espacios en blanco
    rating.columns = rating.columns.str.lower() # en minuscular
    rating.columns = rating.columns.str.strip() # quitar espacios en blanco
    
    print("Procesando Data Rating - Conversion de campo timestamp de object a datetime")
    # Cambio de timestamp tipo object a datetime
    rating["timestamp"] = pd.to_datetime(rating["timestamp"])
    
    print("Procesando Data Rating - Creando campos adicionales como 'year' y 'month'")
    # Creacion de dos columnas year y month 
    rating["year"] =  rating['timestamp'].dt.year
    rating["month"] =  rating['timestamp'].dt.month
    
    print("Procesando Data Rating - Agrupacion por indice para obtener el rating promedio")
    # Agrupacion general por pelicula 
    grupo = rating.groupby(["movieid"])["rating"]
    rating_movies_promedio = grupo.mean()
    rating_movies_conteo = grupo.count()
    
    print("Procesando Data Rating - Seleccion de data para adicionar a la tabla de hecho")
    # Union de promedio y conteo para que sea unido a movies de forma general
    ratings_agg = pd.merge(rating_movies_promedio, rating_movies_conteo, on="movieid", how="left")
    
    print("Procesando Data Rating - Renombrado de columnas")
    # Cambio de nombre de columnas
    ratings_agg = ratings_agg.rename(
        columns={
            "rating_x": "rating_promedio",
            "rating_y": "rating_conteo"
        }
    )
    ratings_agg.reset_index(inplace=True)
    
    print("Procesando Data Rating - Seleccion de data para tabla de dimension ")
    # Creacion de la tablas de dimension 
    # Agrupacion
    grupo = rating.groupby(["movieid","userid", "year","month"])["rating"]
    rating_movies_year_month_promedio = grupo.mean()
    rating_movies_year_month_conteo = grupo.count()
    # Union
    dim_rating = pd.merge(rating_movies_year_month_promedio, rating_movies_year_month_conteo, on=["movieid","userid", "year","month"], how="left")
    
    # Cambio de nombre de columnas
    dim_rating = dim_rating.rename(
        columns={
            "rating_x": "promedio",
            "rating_y": "conteo"
        }
    )
    
    # Creación de un campo indice y relleno con secuencial
    dim_rating["ratingid"] = range(1, len(dim_rating) + 1)
    # dim_rating.reset_index(inplace=True)
    # dim_rating.set_index("ratingid", inplace=True)
    dim_rating.reset_index(inplace=True)
    
    #Eliminado columna Conteo ya que el valor siempre es 1
    dim_rating = dim_rating.drop('conteo', axis=1)
    
    print(dim_rating.head())
        
    return ratings_agg, dim_rating


def join_unique_tags(tags):
    return ', '.join(pd.unique(tags))

def procesar_tags(tags_df):
    """
    Realiza la limpieza  y agrupa los tags, ratings,  de las peliculas manejando los datos
    argumento tag_df,  como dataframe raw 
    retorna la data agrupada por el id de pelicula y tag
    """
    print("-----------------------------------")
    print("Procesando Data Tags")
    
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

    # Convertir la Serie a DataFrame y resetear el índice para que movieid sea una columna
    tags_agg_df = tags_agg.to_frame().reset_index()

    return tags_agg_df
