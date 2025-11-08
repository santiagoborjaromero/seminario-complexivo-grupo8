from pydantic import BaseModel

class User(BaseModel):
    userid: int
    nombre: str | None = None 
    email: str | None = None 
    provincia: str | None = None  
    genero: str | None = None  # M/F
    votos: int | None = 0
    rating: float | None = 0.0