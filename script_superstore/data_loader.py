import pandas as pd

def cargar_datos(path, sheets):
    print(f"Cargando datos desde {path} ")
    
    dataframe_cargados = {}
    
    try:
        for sheet in sheets:
            print(f"Leyendo hoja {sheet} ")
            df_temporal = pd.read_excel(path, sheet_name=sheet)
            dataframe_cargados[sheet] = df_temporal 
        print("Datos se han cargado")
        return dataframe_cargados
    except FileNotFoundError:
        print(f"Archivo {path} no encontrado ")
        return None
    except Exception as err:
        print(f"Error {err}")
        return None
    
