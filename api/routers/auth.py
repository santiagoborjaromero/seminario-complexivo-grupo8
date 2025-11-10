from fastapi import APIRouter, Path, Query, Request
from fastapi.responses import JSONResponse
from typing import Annotated
from api.utils.funciones import load_data
import json

from api.models.auth import Auth

api_routes = APIRouter()
TAG = "Usuarios"

@api_routes.post(
    path="/login",
    summary="Inicio de sesión",
    description="Data de inicio y autorizacion de usuario en el sistema",
    tags=[TAG])
def login(dusuario: Auth):
    try:
        usuario = dusuario.model_dump()
        duser = load_data("usuarios.csv")
        temp = json.loads(duser.to_json(orient='records'))
        user = {}
        for d in temp:
            print(f'{d["email"]} | {d["passwd"]} | {usuario["clave"]}')
            if (d["email"] == usuario["usuario"]) and (str(d["passwd"]) == usuario["clave"]):
                user = {
                    "userid": d["userid"],
                    "nombre": d["nombre"],
                    "email": d["email"],
                    "provincia": d["provincia"],
                    "genero": d["genero"],
                    "votos": d["votos"],
                    "rating": d["rating"],
                }
        
        data = user
        print(data)
        status = True
        message = ""
        if data == {}:
            status = False
            message = f"Usuario no encontrado {usuario["usuario"]} o con credenciales erróneas"
    except Exception as err:
        status = False
        data = []
        message = f"Error: {err}"

    return {"status": status,"data": data, "message": message }