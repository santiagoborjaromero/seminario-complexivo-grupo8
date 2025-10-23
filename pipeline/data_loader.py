import pandas as pd
import os
import time

# ----------------------------------------------------------------------------------    
# Ruta absoluta de la carpeta de donde esta el script 
# ----------------------------------------------------------------------------------    
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def cargar_datos(files):
    df = {}
    
    for file in files:
        print(f"Cargando datos {file}")
        start_time = time.perf_counter()
        try:
            f = os.path.join(SCRIPT_DIR, "..", "data", file)
            df_temporal = pd.read_csv(f, encoding='latin1')
            end_time = time.perf_counter()
            df[file] = df_temporal 
            elapsed_time = end_time - start_time
            print(f"{file} {len(df_temporal)} records, elapsed time: {elapsed_time:.4f} seconds")
        except FileNotFoundError:
            print(f"Archivo {file} no encontrado ")
            return None
        except Exception as err:
            print(f"Error {err}")
            return None
    return df
# # ----------------------------------------------------------------------------------    
# # ¿Este archivo se esta ejecutando desde el usuario o esta importado por otro script?
# # ----------------------------------------------------------------------------------    

# if __name__ == "__main__":
#     #Indica donde está el script actual 
#     print(f"Ejecutando script desde : {os.path.abspath(__file__)}")
    
#     #Llamar a la funcion de arriba para cargar el csv
#     dataframe_juegos = cargar_datos(DATA_PATH)
    
#     if dataframe_juegos is not None:
#         print(f"\n--- Primeras 5 filas ---")
#         print(dataframe_juegos.head())  # IMprimer 5 filas
        
#         print("\n--- Informacion del data frame ---")
#         dataframe_juegos.info(show_counts=True) # ShowCounts -> permite si el archivo es muy grande ayuda a obtener data 

        
