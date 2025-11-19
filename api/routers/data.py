from fastapi import APIRouter, Path, Query, Request
from fastapi.responses import JSONResponse
from typing import Annotated
import numpy as np
import pandas as pd


from api.models.usuario import User
from api.models.movie_form_data import MovieFormData
from api.utils.funciones import load_data
from api.schemas.schema_user import userEntity, usersEntity

data_routes = APIRouter()
TAG = "General"

@data_routes.get(
    path="/data/users", 
    summary="Listado de usuarios", 
    description="Lista de usuarios que han votado en el ultimo año", 
    tags=[TAG])
def usuarios():
    try:
        duser = load_data("usuarios.csv")
        # duser = duser.sort_values("rating_promedio", ascending=False)
        # duser = duser.iloc[:10]
        data = duser.to_json(orient='records')
        print(data)
        # data = duser.to_json(orient='records', indent=4)
        status = True
        message = ""
    except Exception as err:
        status = False
        data = []
        message = f"Error: {err}"
        
    return {"status": status,"data": data, "message": message }

@data_routes.post(
    path="/data/clean_movies", 
    summary="Data limpia de movies", 
    description="Data limpia de movies que incluye ratings, tag, y generos", 
    tags=[TAG])
def movies(form_data: MovieFormData):
    try:
        # Capturando data que viene del filtro 
        fdata = form_data.model_dump()
        orderby = fdata["order_by"]
        genres = fdata["genres"]
        rating_min = fdata["rating_min"]
        rating_max = fdata["rating_max"]
        count_slider_min = fdata["count_slider_min"]
        count_slider_max = fdata["count_slider_max"]
        items_per_page = fdata["items_per_page"]
        movie_title = fdata["movie_title"]
        filter = fdata["filter"]
        userid = fdata["userid"]
        
        print("Filtro", filter)
        # Cargand data Movies
        ddata = load_data("movie_perfil_contenido.csv")
        
        if filter != "Todas":
            print("Cargando tus preferencias")
            rating = load_data("clean_rating.csv")
            
            rating_filtrado = rating[rating['userid'] == userid]
            grupo = rating_filtrado.groupby(["movieid"])["rating"]
            rating_movies_promedio = grupo.mean()
            rating_movies_conteo = grupo.count()
            
            ratings_aggs = pd.merge(rating_movies_promedio, rating_movies_conteo, on="movieid", how="left")
            print("Procesando Data Rating - Renombrado de columnas")
            # Cambio de nombre de columnas
            ratings_aggs = ratings_aggs.rename(
                columns={
                    "rating_x": "rating_usuario_promedio",
                    "rating_y": "rating_usuario_conteo"
                }
            )
            ratings_aggs = ratings_aggs.reset_index()
            print(ratings_aggs.shape)
            newdf = pd.merge(ratings_aggs, ddata, on="movieid", how="left")
            # newdf = newdf.sort_values(by="rating_usuario_conteo", ascending=False)
            print(newdf.shape)
            ddata = newdf.copy()
            
                
        if not movie_title:
            #Filtrado por genero si existe
            if len(genres) > 0:
                print(genres)
                filtro = ddata['genres'].str.split("|").apply(lambda x: any(np.isin(genres, x)))
                ddata = ddata[filtro]
            
            # Filtrado por rating en su rango si el maximo es mayor que 0
            if (rating_max > 0):
                print(rating_min, rating_max)
                if filter == "Todas":
                    filtro = (ddata["rating_promedio"] >= rating_min) & (ddata["rating_promedio"] <= rating_max)
                else:
                    filtro = (ddata["rating_usuario_promedio"] >= rating_min) & (ddata["rating_usuario_promedio"] <= rating_max)
                ddata = ddata[filtro]

            if (count_slider_max > 0):
                print(count_slider_min, count_slider_max)
                if filter == "Todas":
                    print("Slider Todas")
                    filtro = (ddata["rating_conteo"] >= count_slider_min) & (ddata["rating_conteo"] <= count_slider_max)
                else:
                    print("Slider Tus mas votadas")
                    filtro = (ddata["rating_usuario_conteo"] >= count_slider_min) & (ddata["rating_usuario_conteo"] <= count_slider_max)
                ddata = ddata[filtro]
        else:
            print("Titulo:", movie_title)
            filtro = ddata["title"].str.contains(movie_title, case=False)
            ddata = ddata[filtro]
            
        # Ordenado
        print("Ordenando")
        if orderby == "Rating":
            if filter == "Todas":
                ddata = ddata.sort_values(by="rating_promedio", ascending=False)
            else:
                ddata = ddata.sort_values(by="rating_usuario_promedio", ascending=False)
                
        elif orderby == "Popularidad":
            if filter == "Todas":
                ddata = ddata.sort_values(by="rating_conteo", ascending=False)
            else:
                ddata = ddata.sort_values(by="rating_usuario_conteo", ascending=False)
                

        # Columnas 
        # columnas = ddata.columns
        print("Obteniendo Columnas")
        columns = ddata.columns
        col_str = ",".join(columns)
        
        # Limite   
        print("Aplicando imite")
        ddata = ddata.iloc[0:items_per_page]
        # print(ddata)
        
        print("Convirtiendo a JSON")
        ddata = ddata.to_json(orient='records')
        # data = duser.to_json(orient='records', indent=4)
        status = True
        message = col_str
        data = ddata
    except Exception as err:
        status = False
        data = []
        message = f"Error: {err}"
        
    return {"status": status,"data": data, "message": message }

@data_routes.get(
    path="/data/clean_ratings", 
    summary="Data limpia de ratings ", 
    description="Data limpia de ratings ordernada por moveid y usuario id", 
    tags=[TAG])
def contenido():
    try:
        ddata = load_data("clean_rating.csv")
        data = ddata.to_json(orient='records')
        # data = duser.to_json(orient='records', indent=4)
        status = True
        message = ""
    except Exception as err:
        status = False
        data = []
        message = f"Error: {err}"
        
    return {"status": status,"data": data, "message": message }

@data_routes.get(
    path="/data/clean_links", 
    summary="Data limpia de solo de links ", 
    description="Data limpia solo de links", 
    tags=[TAG])
def contenido():
    try:
        ddata = load_data("clean_links.csv")
        data = ddata.to_json(orient='records')
        # data = duser.to_json(orient='records', indent=4)
        status = True
        message = ""
    except Exception as err:
        status = False
        data = []
        message = f"Error: {err}"
        
    return {"status": status,"data": data, "message": message }

@data_routes.get(
    path="/data/genres", 
    summary="Data de generos de peliculas ", 
    description="Data de generos de peliculas", 
    tags=[TAG])
def contenido():
    try:
        ddata = load_data("genres.csv")
        data = ddata.to_json(orient='records')
        status = True
        message = ""
    except Exception as err:
        status = False
        data = []
        message = f"Error: {err}"
        
    return {"status": status,"data": data, "message": message }

# Endpoint para obtener el catálogo de KPI's de Dama
@data_routes.get(
    path="/data/catalog_dama",
    summary="Listado de Kpis de Dama", 
    description="Listado de KPI's de calidad de datos Dama", 
    tags=[TAG])
def catalog_dama():
    try:
        dcatalogDama = load_data("catalog_Dama.csv")
        data = dcatalogDama.to_json(orient='records')
        status = True
        message = ""
    except Exception as err:
        status = False
        data = []
        message = f"Error: {err}"
        
    return {"status": status,"data": data, "message": message }

# Endpoint para obtener el catálogo de KPI's de Dama Movies
@data_routes.get(
    path="/data/movie_dama",
    summary="Listado de Kpis de Dama Movie", 
    description="Listado de KPI's de calidad de datos Dama Movie", 
    tags=[TAG])
def catalog_dama():
    try:
        dcatalogdama = load_data("movie_kpis.csv")
        data = dcatalogdama.to_json(orient='records')
        status = True
        message = ""
    except Exception as err:
        status = False
        data = []
        message = f"Error: {err}"
        
    return {"status": status,"data": data, "message": message }

# Endpoint para obtener el catálogo de KPI's de Dama Ratings
@data_routes.get(
    path="/data/rating_dama",
    summary="Listado de Kpis de Dama Ratings", 
    description="Listado de KPI's de calidad de datos Dama Ratings", 
    tags=[TAG])
def catalog_dama():
    try:
        dcatalogdama = load_data("rating_kpis.csv")
        data = dcatalogdama.to_json(orient='records')
        status = True
        message = ""
    except Exception as err:
        status = False
        data = []
        message = f"Error: {err}"
        
    return {"status": status,"data": data, "message": message }

# Endpoint para obtener el catálogo de KPI's de Dama Tags
@data_routes.get(
    path="/data/tag_dama",
    summary="Listado de Kpis de Dama Tags", 
    description="Listado de KPI's de calidad de datos Dama Tags", 
    tags=[TAG])
def catalog_dama():
    try:
        dcatalogdama = load_data("tag_kpis.csv")
        data = dcatalogdama.to_json(orient='records')
        status = True
        message = ""
    except Exception as err:
        status = False
        data = []
        message = f"Error: {err}"
        
    return {"status": status,"data": data, "message": message }