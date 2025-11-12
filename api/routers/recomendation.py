from fastapi import APIRouter, Path, Query
from typing import Annotated
from api.utils.funciones import load_data
import pandas as pd
from pipeline.data_saving import guardar_informacion
from sklearn.metrics.pairwise import cosine_similarity
from pipeline.data_loader import load_data
import numpy as np


recommed_routes = APIRouter()

def create_query_vector(target_genre, genres_list):
    vec = np.zeros(len(genres_list))
    if target_genre in genres_list:
        idx = genres_list.index(target_genre)
        vec[idx] = 1
    else:
        raise ValueError(f"Género '{target_genre}' no está en la lista.")
    return vec.reshape(1, -1)  # shape: (1, 19)

def recommend_by_genre(target_genre, movies_df, genres_list, top_n=10):
    # Vector de consulta
    query_vec = create_query_vector(target_genre, genres_list)
    # Matriz de características
    X = movies_df[genres_list].values
    # Similitud del coseno entre la consulta y todas las películas
    similarities = cosine_similarity(query_vec, X).flatten()
    # Añadir similitudes al DataFrame temporalmente
    movies_df_temp = movies_df.copy()
    movies_df_temp['similarity'] = similarities
    # Filtrar solo películas que tengan ese género (opcional, pero evita falsos positivos)
    # En teoría, solo las de ese género tendrán similitud > 0
    recommended = movies_df_temp[movies_df_temp[target_genre] == 1]
    # Ordenar por similitud (descendente) y luego por rating_promedio (para priorizar las mejor valoradas)
    recommended = recommended.sort_values(
        by=['similarity', 'rating_promedio', 'rating_conteo'],
        ascending=[False, False, False]
    ).head(top_n)
    
    return recommended

def recommend_collaborative(ratings, user_sim_df, userid, n=10):
    similar_users = user_sim_df[userid].sort_values(ascending=False).index[1:6]  # top 5 similares
    watched = set(ratings[ratings['userid'] == userid]['movieid'])
    candidates = ratings[ratings['userid'].isin(similar_users)]
    candidates = candidates[~candidates['movieid'].isin(watched)]
    recs = candidates.groupby('movieid')['rating'].mean().sort_values(ascending=False).head(n)
    return recs.index.tolist()


@recommed_routes.get(
    path="/recommendations/colaborativa/{userid}/{limit}", 
    summary="Recomendaciones por usuario", 
    description="Recomendacion bajo el modelo de filtrado colaborativo basado en KKN que es el modelo de calculo por vecindad utilizando la similitud del coseno", 
    tags=["Recomendaciones"])
def colab(
        userid: Annotated[int, Path(title="Id del usuario a quien se debe hacer la recomendacion")],
        limit: Annotated[int, Path(title="Número de items a recomendar")]
    ):
    try:
        print("Rating - Cargando data ")
        ratings = load_data("clean_rating.csv")
        print("Movies - Cargando data ")
        movies_original = load_data("movie_perfil_contenido.csv")
        
        # -------------------------------------------
        # FILTRO COLABORATIVO
        # METODO BASADO EN VECINDAD - KNN K-Nearest Neighbors
        # -------------------------------------------
        
        print("Filtro Colaborativo - Rating - Agrupacion 1 por indice para obtener el rating promedio")
        # Agrupacion general por pelicula 
        grupo = ratings.groupby(["movieid"])["rating"]
        rating_movies_promedio = grupo.mean()
        rating_movies_conteo = grupo.count()
        
        print("Procesando Data Rating - Seleccion de data para adicionar a la tabla de hecho")
        # Union de promedio y conteo para que sea unido a movies de forma general
        ratings_aggs = pd.merge(rating_movies_promedio, rating_movies_conteo, on="movieid", how="left")
        
        print("Procesando Data Rating - Renombrado de columnas")
        # Cambio de nombre de columnas
        ratings_aggs = ratings_aggs.rename(
            columns={
                "rating_x": "rating_promedio",
                "rating_y": "rating_conteo"
            }
        )
        ratings_aggs.reset_index(inplace=True)

        print("Filtro Colaborativo - Obteniendo una matriz")
        user_movie_matrix = ratings.pivot(index='userid', columns='movieid', values='rating').fillna(0)
        
        print("Filtro Colaborativo - Calculando el coseno de similaridad")
        user_sim = cosine_similarity(user_movie_matrix)
        
        print("Filtro Colaborativo - Creando el dataframe")
        user_sim_df = pd.DataFrame(user_sim, index=user_movie_matrix.index, columns=user_movie_matrix.index)
        
        print(f"Filtro Colaborativo - Calculando recomendacion para usuario {userid}")
        collab_recs = recommend_collaborative(ratings, user_sim_df, userid, n=limit)
        
        print(f"Filtro Colaborativo - Trabajando con Movies")
        # trabajando con movies
        # col_categoricas =["movieid","title","rating_promedio","rating_conteo","tag","tmdbid"]
        col_categoricas =["movieid", "title", "genres", "tag", "tmdbid"]
        movies = pd.DataFrame(movies_original, columns=col_categoricas)
        movies.reset_index(level=0, inplace=True)
        
        print("Filtro Colaborativo - filtrando data con la recomendacion")
        movies = movies[movies["movieid"].isin(collab_recs)]
        # print(movies.shape)
        
        print("Filtro Colaborativo - Uniendo recomendacion con data del las portadas de las peliculas")
        mr_df = pd.merge(movies, ratings_aggs, left_on="movieid", right_on="movieid", how="left")
        mr_df = mr_df.sort_values(by="rating_conteo", ascending=False)
        ddata = mr_df.to_json(orient='records')
        # print(ddata)
        
        status = True
        data = ddata
        message = ""
    except Exception as err:
        status = False
        data = {}
        message = err
        
    return {"status": status,"data": data, "message": message }


@recommed_routes.get(
    path="/recommendations/contenido/{genero}/{limit}", 
    summary="Recomendaciones por genero", 
    description="Recomendacion bajo el modelo de filtrado por contenido basado en KKN que es el modelo de calculo por vecindad utilizando la similitud del coseno", 
    tags=["Recomendaciones"])
def contenido(
        genero: Annotated[str, Path(title="Genero de peliculas para realizar la recomendacion")],
        limit: Annotated[int, Path(title="Número de items a recomendar")]
    ):
    try:
        # ---------------------------------------------------------
        # FILTRO BASADO EN CONTENIDO
        # ---------------------------------------------------------
        
        print("Filtro Colaborativo - Cargando data Movies")
        movies = load_data("movie_perfil_contenido.csv")
          
        print("Filtro Basando en Contenido - Obtener Generos")
        unique_genres = set() # Usamos un set para guardar los géneros, ya que no permite duplicados
        genres = movies['genres'].str.split(pat='|', expand=True).fillna("")
        # Iteramos sobre cada fila del DataFrame
        for index, row in genres.iterrows():
            for genre in row:
                if genre != '':
                    genre = genre.replace(' ', '_')# Reemplaza espacios en blanco por _
                    genre = genre.replace('-', '')# Reemplaza espacios en blanco por _
                    # genre = genre.replace(r'[^a-zA-Z0-9_]', '') # Reemplaza caracteres especiales
                    unique_genres.add(genre)
                    
        unique_genres_list = list(unique_genres)
        if '(no_genres_listed)' in unique_genres_list:
            unique_genres_list.remove('(no_genres_listed)')
            
        # print(unique_genres_list)
        
        # #Calculo dependiendo el genero
        # recomended = recommend_by_genre(genre, movies_proc, unique_genres_list, top_n=10)
        print("Filtro Basando en Contenido - Recomendacion a base del genero")
        recomended = recommend_by_genre(genero, movies, unique_genres_list, top_n=limit)
        # # top_genre = pd.merge(recomended, links, left_on="movieid", right_on="movieid", how="left")
        mr_df = recomended.sort_values(by="rating_conteo", ascending=False)
        ddata = mr_df.to_json(orient='records')
        # print(ddata)
        
        status = True
        data = ddata
        message = ""
    except Exception as err:
        status = False
        data = {}
        message = err
        
    return {"status": status,"data": data, "message": message }
