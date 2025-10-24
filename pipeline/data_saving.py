import pandas as pd
import os
from .data_loader import SCRIPT_DIR

def guardar_informacion(file, df):
    try:
        cdir = os.path.join(SCRIPT_DIR, "..", "data", "process")
        os.makedirs(cdir, mode=0o777, exist_ok=True)
        
        f = os.path.join(SCRIPT_DIR, "..", "data", "process", file)
        df.to_csv(f, index=False)
        print(f"{f} ha sido guardado !!!")
        return True
    except Exception as err:
        print(f"Error al guardar el archivo {err}")
        return False