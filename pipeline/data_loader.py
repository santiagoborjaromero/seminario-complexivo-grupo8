import pandas as pd
import os

# ----------------------------------------------------------------------------------    
# Ruta absoluta de la carpeta de donde esta el script 
# ----------------------------------------------------------------------------------    
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------------    
# Construir la ruta de los archivos dataset
# ----------------------------------------------------------------------------------    
DATA_PATH = os.path.join(SCRIPT_DIR, "..", "data", "movie.csv")

def cargar_datos(path):
    print(f"Cargando datos desde {path}")
    try:
        df = pd.read_csv(path)
        print("Datos se han cargado")
        return df
    except FileNotFoundError:
        print(f"Archivo {path} no encontrado ")
        return None
    except Exception as err:
        print(f"Error {err}")
        return None
# ----------------------------------------------------------------------------------    
# ¿Este archivo se esta ejecutando desde el usuario o esta importado por otro script?
# ----------------------------------------------------------------------------------    

if __name__ == "__main__":
    #Indica donde está el script actual 
    print(f"Ejecutando script desde : {os.path.abspath(__file__)}")
    
    #Llamar a la funcion de arriba para cargar el csv
    dataframe_juegos = cargar_datos(DATA_PATH)
    
    if dataframe_juegos is not None:
        print(f"\n--- Primeras 5 filas ---")
        print(dataframe_juegos.head())  # IMprimer 5 filas
        
        print("\n--- Informacion del data frame ---")
        dataframe_juegos.info(show_counts=True) # ShowCounts -> permite si el archivo es muy grande ayuda a obtener data 

        
