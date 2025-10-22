import pandas as pd
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
    print (" Tags Agrupados y Limpios")
    return tags_agg

def procesar_ratings(ratings_df):
    ratings_agg = ratings_df.groupby("movieId")["rating"].add(
        rating_promedio="mean",
        total_ratings="count"
    ).reset_index()

    ratings_agg["rating_promedio"]= ratings_agg["rating_promedio"].round(2)
    print(" Rating Promedio y Total")
    return ratings_agg

