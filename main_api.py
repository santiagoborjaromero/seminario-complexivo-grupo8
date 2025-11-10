from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from api.routers.pipeline import pipeline_routes
from api.routers.recomendation import recommed_routes
from api.routers.data import data_routes
from api.routers.auth import api_routes

app = FastAPI(
    debug=True,
    title="Api - Sistema Híbrido de Recomendación de Peliculas",
    summary="Grupo No 8",
    description="Hugo Herrera, Jorge López y Jaime Borja",
    version="0.0.1 beta",
    openapi_url="/api/v1/",
    openapi_tags=[
        {
            "name": "Auth",
            "description": "Procesos de autorización en el sistema",
        },
        {
            "name": "General",
            "description": "Data limpia y procesada como insumo de dasboard y para entrenamiento de machine learning",
        },
        {
            "name": "Recomendaciones",
            "description": "Proceso de Machine Learning para Filtrado Colaborativa y Filtrado por Contenido",
        },
    ]
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(pipeline_routes)
app.include_router(api_routes)
app.include_router(data_routes)
app.include_router(recommed_routes)