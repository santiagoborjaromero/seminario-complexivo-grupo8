import pandas as pd


def crear_ventas_totales(df):
    """
    crea la columna 'ventas_totales' sumando
    las ventas regionales que hay
    """
    print("Creando la columna 'ventas_totales'...")
    
    df["total_sales"] = df["na_sales"] + df["eu_sales"] + df["jp_sales"] + df["other_sales"]
    
    return df


"""

def asignar_generacion(plataforma): 
    if plataforma in ["NES", "2600", "TG16"]:
        return "3ª Gen"
    elif plataforma in ["SNES", "GEN", "GB", "SCD"]:
        return "4ª Gen"
    elif plataforma in ["PS", "N64", "SAT"]:
        return "5ª Gen"
    elif plataforma in ["PS2", "GC", "XB", "GBA"]:
        return "6ª Gen"
    elif plataforma in ["PS3", "X360", "Wii", "PSP", "DS"]:
        return "7ª Gen"
    elif plataforma in ["PS4", "XOne", "WiiU", "3DS", "PSV"]:
        return "8ª Gen"
    elif plataforma in ["PC"]:
        return "PC"
    else:
        return "Otras/Retro"
    

videogames["gen_platform"] = videogames["platform"].apply(asignar_generacion)


def clasificar_user_score(score):
    if pd.isnull(score):
        return "Without score"
    elif score >= 8.5:
        return "Excellent"
    elif score >= 7:
        return "Good"
    elif score >= 5.5:
        return "Regular"
    else:
        return "Bad"
    
    
videogames["classification_user_score"] = videogames["user_score"].apply(clasificar_user_score)

"""