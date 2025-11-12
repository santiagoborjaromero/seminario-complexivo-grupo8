import pandas as pd

print(f"Catálogo DAMA - Contruyendo la data para catalogo")
columnas = ["dama"]
registros = ["Movie", "Tag", "Rating"]

print(f"Catálogo DAMA - Creando Dataframe")
df = pd.DataFrame(registros, columns=columnas)

print(f"Catálogo DAMA - Guardando data/process/catalog_Dama.csv")
df.to_csv("./data/process/catalog_Dama.csv", index=False)