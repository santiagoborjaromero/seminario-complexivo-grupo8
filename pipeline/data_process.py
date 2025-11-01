import pandas as pd
import numpy as np

def procesar_movie(movie_source):
    print("-----------------------------------")
    print("Procesando Data Movie")
    print("Procesando Data Movie - Conversión de campos en minusculas y espacios en blanco")
    
    
    # Establecer campos en minusculas y sin espacios en blanco
    movie_source.columns = movie_source.columns.str.lower() # en minuscular
    movie_source.columns = movie_source.columns.str.strip() # quitar espacios en blanco
    
    #Limpieza de columnas
    # movie_source["title"] = movie_source["title"].str.replace("ÃƒÂ©", "e")
    # movie_source["title"] = movie_source["title"].str.replace("Ã©", "a")
    # movie_source["title"] = movie_source["title"].str.replace("Ã§", "c")
    # movie_source["title"] = movie_source["title"].str.replace("(NyÃ» YÃ´ku no koppu)", "")
    # movie_source["title"] = movie_source["title"].str.replace("(BÃ¼vÃ¶s vadÃ¡sz)", "")
    # movie_source["title"] = movie_source["title"].str.replace("(Ã kÃ¶ldum klaka)", "")
    # movie_source["title"] = movie_source["title"].str.replace("Ã¤", "ä")
    # movie_source["title"] = movie_source["title"].str.replace("Ã©", "é")
    movie_source["title"] = movie_source["title"].str.replace(r"[^a-zA-Z0-9'-()\sáéíóúÁÉÍÓÚ,.]", "", regex=True) # Reemplaza caracteres especiales

    print("Procesando Data Movie - Aplicando One-Hot Encoding a la columna 'genres'")
    movie = movie_source.copy()
    genres_dummies = movie['genres'].str.get_dummies('|') # Separa generos por '|' y crear One-Hot Encoding
    columnas_limpias = genres_dummies.columns.str.replace(' ', '_')# Reemplaza espacios en blanco por _
    columnas_limpias = columnas_limpias.str.replace(r'[^a-zA-Z0-9_]', '', regex=True) # Reemplaza caracteres especiales
    genres_dummies.columns = columnas_limpias #nombra nuevas columnas limpias
    movie = pd.concat([movie, genres_dummies], axis=1) #une dataframes genres a df movie

    return movie, movie_source
    

def procesar_ratings(rating_source):
    print("-----------------------------------")
    print("Procesando Data Rating")
    print("Procesando Data Rating - Conversión de campos en minusculas y espacios en blanco")
    # Establecer campos en minusculas y sin espacios en blanco
    rating_source.columns = rating_source.columns.str.lower() # en minuscular
    rating_source.columns = rating_source.columns.str.strip() # quitar espacios en blanco
    
    print("Procesando Data Rating - Conversion de campo timestamp de object a datetime")
    # Cambio de timestamp tipo object a datetime
    rating_source["timestamp"] = pd.to_datetime(rating_source["timestamp"])
    rating = rating_source.copy()
    
    print("Procesando Data Rating - Creando campos adicionales como 'year' y 'month'")
    # Creacion de dos columnas year y month 
    rating["year"] =  rating['timestamp'].dt.year
    rating["month"] =  rating['timestamp'].dt.month
    
    # -------------------------------------------
    # AG1 
    # Argupacion general 1 insumo para Tabla de Hecho
    # Promedio de raiting y conteo 
    # -------------------------------------------------------------------
    
    print("Procesando Data Rating - Agrupacion 1 por indice para obtener el rating promedio")
    # Agrupacion general por pelicula 
    grupo = rating.groupby(["movieid"])["rating"]
    rating_movies_promedio = grupo.mean()
    rating_movies_conteo = grupo.count()
    
    print("Procesando Data Rating - Seleccion de data para adicionar a la tabla de hecho")
    # Union de promedio y conteo para que sea unido a movies de forma general
    ratings_agg1 = pd.merge(rating_movies_promedio, rating_movies_conteo, on="movieid", how="left")
    
    print("Procesando Data Rating - Renombrado de columnas")
    # Cambio de nombre de columnas
    ratings_agg1 = ratings_agg1.rename(
        columns={
            "rating_x": "rating_promedio",
            "rating_y": "rating_conteo"
        }
    )
    ratings_agg1.reset_index(inplace=True)
    
    # -------------------------------------------------------------------
    # AG2
    # Argupacion general 2 insumo para Tabla de Hecho
    # Promedio de raiting y conteo 
    # -------------------------------------------------------------------
    print("Procesando Data Rating - Agrupacion 2 por indice para obtener el rating promedio por pelicula y año")
    df_year = rating.groupby(["movieid","year"]).agg({"rating": "mean"})
    # print(df_year)
    df_year.reset_index(inplace=True)
    df_year.set_index("movieid", inplace=True)
    
    print("Procesando Data Rating - Agrupacion 2 - Creacion de tabla pivot")
    df_year_pivot = df_year.pivot(columns='year', values=['rating'])
    
    print("Procesando Data Rating - Agrupacion 2 - Reemplazo valores NaN")
    df_year_pivot = df_year_pivot.replace(np.nan, 0)
    # print(df_year_pivot)
    
    df_year_pivot = df_year_pivot.reset_index()
    # print(df_year_pivot)
    df_year_pivot.rename(columns={'movieid': 'movieid'}, inplace=True) 
    
    print("Procesando Data Rating - Agrupacion 2 - Cambio de multiples headers a uno solo")
    columns = [col[1] if isinstance(col, tuple) else col for col in df_year_pivot.columns]
    columns[0] = "movieid"
    df_year_pivot.columns = columns
    # print(df_year_pivot)
    
    print("Procesando Data Rating - Agrupacion 2 - Listado de columnas por año")
    year_cols = [c for c in df_year_pivot.columns if isinstance(c, str) and c.isdigit()]
    for col in year_cols:
        df_year_pivot[col] = pd.to_numeric(df_year_pivot[col], errors='coerce')
    
    # print(df_year_pivot)
    
    # # Union AG 1 y AG 2
    print("Procesando Data Rating - Union Agrupacion 1 y 2")
    ratings_agg_temp= pd.merge(ratings_agg1, df_year_pivot, on="movieid", how="left")
    ratings_agg_temp = ratings_agg_temp.replace(np.nan, 0)
    print("Procesando Data Rating - Eliminado de duplicados")
    # ratings_agg = ratings_agg_temp.drop_duplicates(subset=['movieid'])
    ratings_agg = ratings_agg_temp
    # print(ratings_agg)
    
    
    # -------------------------------------------------------------------
    # Tabla dimension 
    # Promedio de raiting y conteo 
    # -------------------------------------------------------------------
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
    
    # print(dim_rating.head())
        
    return ratings_agg, dim_rating, rating_source


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
    
    # Cambio de timestamp tipo object a datetime
    tags_df["timestamp"] = pd.to_datetime(tags_df["timestamp"])
    
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
    
    # #Agrupacion de tags
    # tags_agg = df_strings.groupby('movieid')['tag'].apply(join_unique_tags)

    # # Convertir la Serie a DataFrame y resetear el índice para que movieid sea una columna
    # tags_agg_df = tags_agg.to_frame().reset_index()

    return df_strings
