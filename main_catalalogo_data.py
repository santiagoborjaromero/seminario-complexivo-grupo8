import pandas as pd

columnas = ["dama"]
registros = ["Movie", "Tag", "Rating"]

df = pd.DataFrame(registros, columns=columnas)
df.to_csv("./data/process/catalog_Dama.csv", index=False)