from fastapi import APIRouter, Path, Query
from typing import Annotated
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from numpy.linalg import svd

from api.utils.funciones import load_data

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
        # Obteniendo una matriz
        user_movie_matrix = ratings.pivot(index='userid', columns='movieid', values='rating').fillna(0)
        
        print("Filtro Colaborativo - Calculando el coseno de similaridad")
        # Calculando el coseno de similaridad
        user_sim = cosine_similarity(user_movie_matrix)
        
        print("Filtro Colaborativo - Creando el dataframe")
        # Creando el dataframe
        user_sim_df = pd.DataFrame(user_sim, index=user_movie_matrix.index, columns=user_movie_matrix.index)
        
        print(f"Filtro Colaborativo - Calculando recomendacion para usuario {userid}")
        # Calculando recomendacion para usuario
        collab_recs = recommend_collaborative(ratings, user_sim_df, userid, n=limit)
        
        print(f"Filtro Colaborativo - Trabajando con Movies")
        # trabajando con movies
        col_categoricas =["movieid", "title", "genres", "tag", "tmdbid"]
        movies = pd.DataFrame(movies_original, columns=col_categoricas)
        movies.reset_index(level=0, inplace=True)
        
        print("Filtro Colaborativo - filtrando data con la recomendacion")
        # filtrando data con la recomendacion
        movies = movies[movies["movieid"].isin(collab_recs)]
        # print(movies.shape)
        
        print("Filtro Colaborativo - Uniendo recomendacion con data del las portadas de las peliculas")
        # Uniendo recomendacion con data del las portadas de las peliculas
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


@recommed_routes.get(
    path="/recommendations/svd/{userid}/{limit}", 
    summary="Recomendaciones por usuario con el metodo SVD", 
    description="Recomendacion bajo el modelo de filtrado colaborativo basado en KKN que es el modelo de calculo por vecindad utilizando la similitud del coseno", 
    tags=["Recomendaciones"])
def methodsvd(
        userid: Annotated[int, Path(title="Id del usuario a quien se debe hacer la recomendacion")],
        limit: Annotated[int, Path(title="Número de items a recomendar")]
    ):
        
    try:
        print("Rating - Cargando data ")
        #Rating - Cargando data 
        ratings_original = load_data("clean_rating.csv")
        
        print("Movies - Cargando data ")
        # Movies - Cargando data 
        movies_original = load_data(
            "movie_perfil_contenido.csv",
            # usecols = ["movieid", "title", "tmdbid", "genres"]
        )
        
        # -------------------------------------------
        # FILTRO BASADO EN CONTENIDO
        # METODO SVD
        # -------------------------------------------
        print("SVD - Uniendo dataframes ")
        df = pd.merge(ratings_original, movies_original, on='movieid')
        
        # MATRIZ - TABLA CRUZADA
        print("SVD - Creando tabla cruzada o pivot ")
        user_item_matrix = df.pivot_table(index='userid', columns='movieid', values='rating').fillna(0)

        print("SVD - aplicando SVD ")
        # Aplicacion de SVD Singular Value Decomposition
        # R=U×Σ×V^T
        #       R -> matriz original a descomponer
        #       U -> matriz ortogonalde dimension de m x m (donde m, es el numero de filas de R) y U son los vectores singulares izquierdois
        #       Σ -> Es una matriz diagonal de dimensiones m x n (donde nes el número de columnas de R 
        #            que contiene los valores singulares en su diagonal, ordenados de mayor a menor. El resto de los elementos son cero.
        #       V^T -> Es la traspuesta de una matriz ortogonal llamada V. Las columnas de V son los vectores singulares derechos, 
        #            y sus filas corresponden a las columnas de V^T
        
        # to_numpy() es un método para convertir un objeto de tabla en un array de NumPy
        
        print("SVD - Obteniendo valores de formula R=U×Σ×V^T ")
        # Obteniendo valores 
        R = user_item_matrix.to_numpy()
        U, sigma, Vt = svd(R, full_matrices=False)
        
        print("SVD - Obteniendo recomendacion")
        # Obteniendo recomendacion
        # Numero de Vecinos 50
        k = 50
        
        # np.diag sirve para extraer la diagonal de una matriz 
        sigma_k = np.diag(sigma[:k])

        # np.dot es una funciona de NumPy usada para calcular el valor escalar de dos arrays
        R_approx = np.dot(np.dot(U[:, :k], sigma_k), Vt[:k, :])

        # Creando Dataframe
        R_pred_df = pd.DataFrame(R_approx, 
                                index=user_item_matrix.index, 
                                columns=user_item_matrix.columns)
        R_pred_df.head()
        
        # LOC se utiliza para filtrar por indices
        user_ratings = user_item_matrix.loc[userid]
        user_predictions = R_pred_df.loc[userid]

        # Recommend top 10 unrated movies
        unrated = user_ratings[user_ratings == 0]
        recommendations = user_predictions[unrated.index].sort_values(ascending=False).head(10)
        
        print("SVD - Uniendo resultados con base movies")
        recommendations.reset_index( inplace=False )
        rdf = pd.merge(recommendations, movies_original, on="movieid", how="left")
        
        ddata = rdf.to_json(orient='records')
        
        status = True
        data = ddata
        message = ""
    except Exception as err:
        status = False
        data = {}
        message = err
        
    return {"status": status,"data": data, "message": message }



@recommed_routes.get(
    path="/recommendations/pelicula/{movie_title}", 
    summary="Recomendaciones por una pelicula determinada", 
    description="Recomendacion bajo el modelo de filtrado colaborativo basado en KKN que es el modelo de calculo por vecindad utilizando la similitud del coseno", 
    tags=["Recomendaciones"])
def colab(
        movie_title: Annotated[str, Path(title="Nombre de la pelicula para hacer la recomendacion")]
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
        
        print("Procesando Data Rating - Union Ratings y Movies")
        # Union de promedio y conteo para que sea unido a movies de forma general
        mov_user_df = pd.merge(ratings, movies_original, on="movieid", how="left")
        mov_user_pv = mov_user_df.pivot_table(index = ["userid"],columns = ["title"],values = "rating").fillna(0)
        movie = mov_user_pv[movie_title]
        
        print("Procesando Data Rating - Por Correlacion")
        movie_corr = mov_user_pv.corrwith(movie)
        movie_corr = movie_corr.sort_values(ascending=False).reset_index()
        
        print("Filtro Colaborativo - Uniendo recomendacion con data del las portadas de las peliculas")
        mr_df = pd.merge(movie_corr, movies_original, on="title", how="left").head(6)
        ddata = mr_df.to_json(orient='records')
        # print(ddata)
        print("Filtro Colaborativo - Enviando")
        
        status = True
        data = ddata
        message = ""
    except Exception as err:
        status = False
        data = {}
        message = err
        
    return {"status": status,"data": data, "message": message }

