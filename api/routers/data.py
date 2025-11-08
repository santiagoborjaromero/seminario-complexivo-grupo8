from fastapi import APIRouter, Path, Query
from fastapi.responses import JSONResponse
from typing import Annotated

from api.models.usuario import User
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

@data_routes.get(
    path="/data/clean_movies", 
    summary="Data limpia de movies", 
    description="Data limpia de movies que incluye ratings, tag, y generos", 
    tags=[TAG])
def movies():
    try:
        ddata = load_data("movie_perfil_contenido.csv")
        duser = ddata.sort_values("rating_conteo", ascending=False)
        duser = duser.iloc[0:10]
        print(duser)
        data = duser.to_json(orient='records')
        # data = duser.to_json(orient='records')
        # data = duser.to_json(orient='records', indent=4)
        status = True
        message = ""
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

