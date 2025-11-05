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
        print(f"------------------------------------------")
        print(f"Importando datos desde {file}")
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



def load_data(file_path):
    BASE_DIR = os.getcwd() 
    DATA_PROCESS_DIR = os.path.join(BASE_DIR, 'data', 'process')
    PROCESSED_FILE = os.path.join(DATA_PROCESS_DIR, file_path)
    try:
        df = pd.read_csv(PROCESSED_FILE, encoding='latin1')
        return df
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {PROCESSED_FILE}")
        return None