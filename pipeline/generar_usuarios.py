import pandas as pd
import missingno as msno
import numpy as np
from faker import Faker
import random

def sin_tilde(email):
    replacements = (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"))
    for a, b in replacements:
        email = email.replace(a, b).replace(a.upper(), b.upper())
    return email

fake = Faker('es_ES')  # o 'es_ES' 
rango = range(1,138494)
    
data = []
userid = 0
for i in rango:
    nombre = fake.name()
    email = nombre.lower().replace(" ", ".") + "@ejemplo.com"
    genero = random.choice(['M', 'F'])
    passwd="1234"
    provincia = random.choice( [
        "Azuay",
        "Bolívar",
        "Cañar",
        "Carchi",
        "Chimborazo",
        "Cotopaxi",
        "El Oro",
        "Esmeraldas",
        "Galápagos",
        "Guayas",
        "Imbabura",
        "Loja",
        "Los Ríos",
        "Manabí",
        "Morona Santiago",
        "Napo",
        "Orellana",
        "Pastaza",
        "Pichincha",
        "Santa Elena",
        "Santo Domingo de los Tsáchilas",
        "Sucumbíos",
        "Tungurahua",
        "Zamora Chinchipe"
    ])
    
    fila = [i, nombre, email, passwd, genero, provincia]
    data.append(fila)

columnas = ['userid', 'nombre', 'email', 'passwd', 'genero', 'provincia'] 
df = pd.DataFrame(data, columns=columnas)

df['email'] = df['email'].apply(sin_tilde)

df_user = df.copy()

# df_user_original = pd.read_csv(r"./data/usuarios.csv", encoding="utf8")
df_rating = pd.read_csv(r"./data/process/clean_rating.csv", encoding="utf8")

# df_user = df_user_original[["userid","nombre","email","genero"]]
# df_rating = df_rating_origin[df_rating_origin["year"] == 2015]

df_rating_last_year_promedio = df_rating.groupby("userid").agg({"rating": "mean"})
df_rating_last_year_votos = df_rating.groupby("userid").agg({"rating": "count"})

df1 = pd.merge(df_rating_last_year_votos, df_rating_last_year_promedio, on="userid", how="left")
df1 = df1.rename(
    columns={
        "rating_x": "votos",
        "rating_y": "rating",
    }
)
df = pd.merge(df_user, df1, on="userid", how="left")
df = df.sort_values(by="votos", ascending=False)

df = df.dropna(subset=["rating","votos"], how="all")
# print(df.shape)

df.to_csv("./data/process/usuarios.csv", index=False)