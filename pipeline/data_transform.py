import pandas as pd

"""Se crea columan perfil de contenido
    Argumentos los dataframes procesados y dataframe movies
    retornna Data limpia, llena con 0 en caso de nulos
"""

def transformar_datos(movies_df, tags_agrupados_df, ratings_agrupados_df):
    print("Fuciond de Dataframes")
    df_final = movies_df
    df_final = pd.merge(df_final, tags_agrupados_df, on="movieId", how="left")
    df_final["tags_agrupados"]=df_final["tags_agrupados"].fillna('')
    df_final["rating_promedio"]=df_final["rating_promedio"].fillna(0)
    df_final["total_ratings"]=df_final["total_ratings"].fillna(0).astype(int)
    df_final["genres"]=df_final["genres"].str.replace('|', ' ', regex=False)
    df_final["perfil_de_contenido"]=df_final["genres"]+ ' ' + df_final["tags_agrupados"]
    df_final["perfil_de_contenido"]=df_final["perfil_de_contenido"].str.replace(r'\s+', ' ', regex=True).str.strip()
    print ("Transformación completada")

    return df_final