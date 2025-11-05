import pandas as pd
import numpy as np

from pipeline.data_saving import guardar_informacion
from sklearn.metrics.pairwise import cosine_similarity

from pipeline.data_loader import load_data
from pipeline.data_saving import guardar_informacion

RATINGS = "rating.csv"
# USERID = 31
USERID = 284
GENRE = "Adventure"

def recommend_collaborative(user_sim_df, userid, n=10):
    similar_users = user_sim_df[userid].sort_values(ascending=False).index[1:6]  # top 5 similares
    watched = set(ratings[ratings['userid'] == userid]['movieid'])
    candidates = ratings[ratings['userid'].isin(similar_users)]
    candidates = candidates[~candidates['movieid'].isin(watched)]
    recs = candidates.groupby('movieid')['rating'].mean().sort_values(ascending=False).head(n)
    return recs.index.tolist()

def recommend_movies(movie_title, df, similarity_matrix, top_n=10):
    # Encuentra el índice de la película
    idx = df[df['title'] == movie_title].index
    if len(idx) == 0:
        print("Película no encontrada.")
        return None
    idx = idx[0]

    # Obtiene las similitudes para esa película
    sim_scores = list(enumerate(similarity_matrix[idx]))
    # Ordena por similitud (descendente), excluye la misma película
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    # Obtiene los índices de las películas recomendadas
    movie_indices = [i[0] for i in sim_scores]
    # Devuelve las películas recomendadas
    return df.iloc[movie_indices][['title', 'genres']]

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
    # recommended = recommended.sort_values(
    #     by=['similarity', 'rating_promedio', 'rating_conteo'],
    #     ascending=[False, False, False]
    # ).head(top_n)
    recommended = recommended.sort_values(
        by=['similarity'],
        ascending=[False]
    ).head(top_n)
    
    return recommended

if __name__ == "__main__":
    # RATING
    print("Rating - Cargando data ")
    ratings_original = load_data("rating.csv")
    print("Rating - Cambiando timestamp de object a datatime")
    ratings_original["timestamp"] = pd.to_datetime(ratings_original["timestamp"])
    print("Rating - Calculando el ultimo año de ratings")
    YEAR_FILTER = ratings_original["timestamp"].dt.year.max()
    print("Rating - Filtrando data del ultimo año")
    ratings = ratings_original[ratings_original["timestamp"].dt.year >= YEAR_FILTER]
    
    print("Tags - Cargando data ")
    tags = load_data("tag.csv")
    print("Tags - Cambiando timestamp de object a datatime")
    tags["timestamp"] = pd.to_datetime(tags["timestamp"])
    print("Tags - Filtrando data del ultimo año")
    tags = tags[tags["timestamp"].dt.year >= YEAR_FILTER]
    
    print("Movies - Cargando data ")
    movies_original = load_data("movie.csv")
    
    print("Rating - Cargando data ")
    links = load_data("links.csv")
    
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
    
    print("Filtro Colaborativo - Calculando recomendacion para usuario {USERID}")
    collab_recs = recommend_collaborative(user_sim_df, USERID, n=10)
    
    print("Filtro Colaborativo - filtrando data con la recomendacion")
    movies = movies_original.copy()
    movies = movies[movies["movieid"].isin(collab_recs)]
    print(movies.shape)
    
    print("Filtro Colaborativo - Uniendo recomendacion con data del las portadas de las peliculas")
    mr_df = pd.merge(movies, ratings_aggs, left_on="movieid", right_on="movieid", how="left")
    vecindad_por_usuario = pd.merge(mr_df, links, left_on="movieid", right_on="movieid", how="left")
    
    # Guardar Archivo
    print("Filtro Colaborativo - Guardando Archivo")
    guardar_informacion("data_por_vecindad.csv", vecindad_por_usuario)
    
    # ---------------------------------------------------------
    # FILTRO BASADO EN CONTENIDO
    # ---------------------------------------------------------
    print("Filtro Basando en Contenido - Obtener Generos")
    unique_genres = set() # Usamos un set para guardar los géneros, ya que no permite duplicados
    genres = movies['genres'].str.split(pat='|', expand=True).fillna("")
    # Iteramos sobre cada fila del DataFrame
    for index, row in genres.iterrows():
        for genre in row:
            if genre != '':
                genre = genre.replace(' ', '_')# Reemplaza espacios en blanco por _
                genre = genre.replace('-', '')# Reemplaza espacios en blanco por _
                genre = genre.replace(r'[^a-zA-Z0-9_]', '') # Reemplaza caracteres especiales
                unique_genres.add(genre)
                
    unique_genres_list = list(unique_genres)
    if '(no_genres_listed)' in unique_genres_list:
        unique_genres_list.remove('(no_genres_listed)')
        
    
    print("Filtro Basando en Contenido - Aplicando One-Hot Encoding a la columna 'genres'")
    
    genres_dummies = movies_original['genres'].str.get_dummies('|') # Separa generos por '|' y crear One-Hot Encoding
    columnas_limpias = genres_dummies.columns.str.replace(' ', '_')# Reemplaza espacios en blanco por _
    columnas_limpias = columnas_limpias.str.replace(r'[^a-zA-Z0-9_]', '', regex=True) # Reemplaza caracteres especiales
    genres_dummies.columns = columnas_limpias #nombra nuevas columnas limpias
    movies_proc = pd.concat([movies_original, genres_dummies], axis=1)
    
    genero = GENRE
    #Calculo dependiendo el genero
    recomended = recommend_by_genre(genero, movies_proc, unique_genres_list, top_n=10)

    top_genre = pd.merge(recomended, links, left_on="movieid", right_on="movieid", how="left")
    
    # Guardar Archivo
    print("Filtro Basando en Contenido - Guardando Archivo")
    guardar_informacion("data_por_contenido.csv", top_genre)
    