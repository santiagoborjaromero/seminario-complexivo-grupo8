from pydantic import BaseModel

class Auth(BaseModel):
    usuario: str | None = None 
    clave: str | None = None 