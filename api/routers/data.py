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
        # Capturando data del filtro
        fdata = form_data.model_dump()
        orderby = fdata["order_by"]
        genres = fdata["genres"]
        rating_min = fdata["rating_min"]
        rating_max = fdata["rating_max"]
        count_slider_min = fdata["count_slider_min"]
        count_slider_max = fdata["count_slider_max"]
        items_per_page = fdata["items_per_page"]
        movie_title = fdata["movie_title"]
        
        #Cargand data
        data = load_data("movie_perfil_contenido.csv")
        
        # Seleccionando las columnas necesarias
        col_categoricas = ['movieid', 'title', 'genres', 'rating_promedio', 'rating_conteo', 'tag', 'tmdbid']
        ddata = pd.DataFrame(data, columns=col_categoricas)
        ddata.reset_index(level=0, inplace=True)
        # ddata.reset_index()
        print(movie_title)
        print(ddata)
        
        if not movie_title:
            #Filtrado por genero si existe
            if len(genres) > 0:
                print(genres)
                filtro = ddata['genres'].str.split("|").apply(lambda x: any(np.isin(genres, x)))
                ddata = ddata[filtro]
            
            # Filtrado por rating en su rango si el maximo es mayor que 0
            if (rating_max > 0):
                print(rating_min, rating_max)
                filtro = (ddata["rating_promedio"] >= rating_min) & (ddata["rating_promedio"] <= rating_max)
                ddata = ddata[filtro]

            if (count_slider_max > 0):
                print(count_slider_min, count_slider_max)
                filtro = (ddata["rating_conteo"] >= count_slider_min) & (ddata["rating_conteo"] <= count_slider_max)
                ddata = ddata[filtro]
        else:
            print("Titulo:", movie_title)
            filtro = ddata["title"].str.contains(movie_title, case=False)
            ddata = ddata[filtro]
            
        # Ordenado
        if orderby == "Rating":
            ddata = ddata.sort_values(by="rating_promedio", ascending=False)
        elif orderby == "Popularidad":
            ddata = ddata.sort_values(by="rating_conteo", ascending=False)
            
        # Limite   
        ddata = ddata.iloc[0:items_per_page]
        print(ddata)
        
        ddata = ddata.to_json(orient='records')
        # data = duser.to_json(orient='records', indent=4)
        status = True
        message = ""
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

