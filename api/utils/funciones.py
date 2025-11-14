import os
import pandas as pd

def load_data(file_path):
    base_dir = os.getcwd() 
    data_process_dir = os.path.join(base_dir, 'data', 'process')
    processed_file = os.path.join(data_process_dir, file_path)
    print(processed_file)
    try:
        df = pd.read_csv(processed_file, encoding='utf8')
        return df
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {processed_file}")
        return None