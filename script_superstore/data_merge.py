import pandas as pd

def unir_df(df):
      
    print("Uniendo")
    
    df_completo = pd.merge(df["Orders"], df["Returned"], on="Order ID", how="left")
    df_completo = pd.merge(df_completo, df["People"], on="Region", how="left")
    
    return df_completo
    
def guardar(path, df):
    df.to_csv(path, index=False)
    
def limpiando(df):
    df["Returned"] = df["Returned"].fillna("No")
    return df   
