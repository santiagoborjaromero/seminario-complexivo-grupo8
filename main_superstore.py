import pandas as pd
import numpy as np
import os
from script_superstore.data_loader import cargar_datos
from script_superstore.data_merge import unir_df, limpiando, guardar

# ----------------------------------------------------------------------------------    
# Ruta absoluta de la carpeta de donde esta el script 
# ----------------------------------------------------------------------------------    
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------------    
# Construir la ruta de los archivos dataset
# ----------------------------------------------------------------------------------    
DATA_PATH = os.path.join(SCRIPT_DIR, ".", "data", "Sample-Superstore.xls")
COMPILED_FILE = os.path.join(SCRIPT_DIR, ".", "data", "SampleSuperstoreCompleto.csv")

# ----------------------------------------------------------------------------------    
# ¿Este archivo se esta ejecutando desde el usuario o esta importado por otro script?
# ----------------------------------------------------------------------------------    

if __name__ == "__main__":
    #Indica donde está el script actual 
    print(f"Ejecutando script desde : {os.path.abspath(__file__)}")
    
    sheets = ["Orders", "Returns", "People"]

    #Llamar a la funcion de arriba para cargar el csv
    diccionario_dataframes = cargar_datos(DATA_PATH, sheets=sheets)
    
    diccionario_dataframes = limpiando(diccionario_dataframes)
    diccionario_dataframes = unir_df(diccionario_dataframes)
    
    guardar(COMPILED_FILE, diccionario_dataframes)
    
    # if diccionario_dataframes is not None:
    #     for sheet, df in diccionario_dataframes.items():

    #         print(f"\n--- Primeras 5 filas {sheet} ---")
    #         print(df.head())  # IMprimer 5 filas
            
    #         print("\n--- Informacion del data frame {sheet} ---")
    #         df.info(show_counts=True) # ShowCounts -> permite si el archivo es muy grande ayuda a obtener data 


