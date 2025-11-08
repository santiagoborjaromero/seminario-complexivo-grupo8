import pandas as pd
import missingno as msno
import numpy as np

df_user_original = pd.read_csv(r"./data/usuarios.csv", encoding="utf8")
df_rating_origin = pd.read_csv(r"./data/process/procesados_ratings.csv", encoding="utf8")

df_user = df_user_original[["userid","nombre","email","genero"]]
df_rating = df_rating_origin[df_rating_origin["year"] == 2015]

df_rating_last_year_promedio = df_rating.groupby("userid").agg({"promedio": "mean"})
df_rating_last_year_votos = df_rating.groupby("userid").agg({"promedio": "count"})

df1 = pd.merge(df_rating_last_year_votos, df_rating_last_year_promedio, on="userid", how="left")
df1 = df1.rename(
    columns={
        "promedio_x": "votos",
        "promedio_y": "rating",
    }
)
df = pd.merge(df_user, df1, on="userid", how="left")
df = df.sort_values(by="votos", ascending=False)

df = df.dropna(subset=["rating","votos"], how="all")
# print(df.shape)

df.to_csv("./data/process/usuarios.csv", index=False)