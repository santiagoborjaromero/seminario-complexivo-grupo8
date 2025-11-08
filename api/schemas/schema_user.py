def userEntity(item) -> dict:
    return{
        "userid": item["userid"],
        "nombre": item["nombre"],
        "email": item["email"],
        "provincia": item["provincia"],
        "genero": item["genero"],
        "votos": item["votos"],
        "rating": item["rating"],
    }


def usersEntity(entity) -> list:
    return [userEntity(item) for item in entity]