import pandas as pd
import os
from .data_loader import SCRIPT_DIR

def guardar_informacion(file, df):
    f = os.path.join(SCRIPT_DIR, "..", "data", file)
    df.to_csv(f)
    print(f"{file} ha sido guardado")