from fastapi import APIRouter

pipeline_routes = APIRouter()

@pipeline_routes.get("/saludo", summary="Saludo", description="Es un saludo", tags=["Pipeline"])
def saludo():
    return "hello"
