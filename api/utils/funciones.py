import os
import pandas as pd

def load_data(file_path):
    BASE_DIR = os.getcwd() 
    DATA_PROCESS_DIR = os.path.join(BASE_DIR, 'data', 'process')
    PROCESSED_FILE = os.path.join(DATA_PROCESS_DIR, file_path)
    # print(PROCESSED_FILE)
    try:
        df = pd.read_csv(PROCESSED_FILE, encoding='utf8')
        return df
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {PROCESSED_FILE}")
        return None