from fastapi import APIRouter, Path, Query
from typing import Annotated

recommed_routes = APIRouter()

@recommed_routes.get(
    path="/recommendations/colaborativa/{user_id}", 
    summary="Recomendaciones por usuario", 
    description="Recomendacion bajo el modelo de filtrado colaborativo basado en KKN que es el modelo de calculo por vecindad utilizando la similitud del coseno", 
    tags=["Recomendaciones"])
def knn(
    item_id: Annotated[int, Path(title="The ID of the item to get")],
    q: Annotated[str | None, Query(alias="item-query")] = None,
):
    return "hello"

@recommed_routes.get(
    path="/recommendations/contenido/{genre}", 
    summary="Recomendaciones por genero", 
    description="Recomendacion bajo el modelo de filtrado por contenido basado en KKN que es el modelo de calculo por vecindad utilizando la similitud del coseno", 
    tags=["Recomendaciones"])
def contenido():
    return "hello"
