
# -*- coding: utf-8 -*-
"""
movies_clean_kpis_commented.py
Limpia movies.csv, calcula KPIs (DAMA) y guarda:
 - Excel: movies_report.xlsx (hojas: KPIs_movies, Clean_movies)
 - CSV:   movies_clean.csv, movies_kpis.csv
Uso:
  python movies_clean_kpis_commented.py --in movies.csv --out_xlsx movies_report.xlsx --out_clean_csv movies_clean.csv --out_kpis_csv movies_kpis.csv
"""
import pandas as pd  # Librería principal para manipulación de datos
import numpy as np   # Para operaciones numéricas y NaN
import argparse      # Para capturar argumentos de línea de comandos

NOW = pd.Timestamp.utcnow()  # Marca temporal "ahora" (UTC) para validar años/fechas

def pct(ok, total):
    """Calcula porcentaje con 2 decimales, protegiendo división por cero."""
    return float(round(100.0 * (ok / total if total else 0), 2))

def kpi_row(name, val, total, target=None, note=""):
    """Retorna un dict estandarizado para una fila de KPI."""
    return {"Tabla": "movies", "KPI": name, "Valor_%": val, "Total_registros": total, "Meta_%": target, "Notas": note}

def safe_read_csv(path):
    """Lee CSV tolerando delimitador ',' o ';'."""
    try:
        return pd.read_csv(path)          # Primer intento: coma
    except Exception:
        return pd.read_csv(path, sep=';') # Segundo intento: punto y coma

def clean_and_kpis_movies(df_movies: pd.DataFrame):
    """Aplica limpieza y calcula KPIs sobre el DataFrame de movies."""
    df = df_movies.copy()                                 # Trabajamos sobre copia para no mutar el original
    cols = {c.lower(): c for c in df.columns}             # Mapa de nombres en minúsculas → nombre real
    movieId = cols.get("movieid", "movieId" if "movieId" in df.columns else df.columns[0])  # Detecta columna movieId
    title   = cols.get("title", "title")                  # Detecta columna title
    genres  = cols.get("genres", "genres")                # Detecta columna genres

    df[movieId] = pd.to_numeric(df[movieId], errors="coerce")  # Convierte movieId a numérico, inválidos → NaN
    df[title]   = df[title].astype(str).str.strip()            # Fuerza a str y recorta espacios
    df[genres]  = df[genres].astype(str).str.strip()           # Idem para géneros

    n = len(df)                                         # Total de registros
    kpis = []                                           # Lista acumuladora de KPIs

    # KPI Unicidad de movieId
    kpis.append(kpi_row("% movieId únicos",
                        100.0 if df[movieId].is_unique else pct(df.drop_duplicates(subset=[movieId]).shape[0], n),
                        n, 100))

    # KPI Completitud de título
    kpis.append(kpi_row("% títulos no nulos", pct(df[title].notna().sum(), n), n, 100))

    # KPI Integridad de géneros (no vacíos)
    has_genre = df[genres].replace({"nan": np.nan}).notna() & (df[genres].str.len() > 0)
    kpis.append(kpi_row("% películas con género", pct(has_genre.sum(), n), n, 100))

    # KPI Consistencia de formato de géneros (palabras separadas por '|')
    genre_format_ok = df[genres].str.fullmatch(r"[A-Za-z][A-Za-z\-]*?(?:\|[A-Za-z][A-Za-z\-]*)*", na=False)
    kpis.append(kpi_row("% géneros formato estándar", pct(genre_format_ok.sum(), n), n, 98))

    # KPI Razonabilidad/Exactitud simple: año entre paréntesis y razonable
    year_extract = df[title].str.extract(r"\((\d{4})\)")[0]      # Extrae año si viene como (YYYY)
    year_num = pd.to_numeric(year_extract, errors="coerce")      # Convierte a numérico
    year_ok = year_num.between(1900, NOW.year + 1)               # Rango razonable
    kpis.append(kpi_row("% año en título válido", pct(year_ok.fillna(False).sum(), n), n, 95))

    # --- Limpieza básica ---
    df_clean = df.loc[df[movieId].notna()].drop_duplicates(subset=[movieId]).copy()  # Quita movieId nulos y duplicados
    df_clean = df_clean.loc[df_clean[title].str.len() > 0].copy()                     # Quita títulos vacíos

    # Normaliza los géneros (capitaliza cada token)
    def normalize_genres(s: str):
        if pd.isna(s) or not s:
            return s
        toks = [t.strip().capitalize() for t in str(s).split("|") if t.strip()]
        return "|".join(toks)

    df_clean[genres] = df_clean[genres].apply(normalize_genres)  # Aplica normalización

    kpi_df = pd.DataFrame(kpis)             # KPIs en DataFrame
    return df_clean, kpi_df                 # Devuelve limpios + KPIs

def main():
    # Parser de argumentos para rutas de entrada/salida
    ap = argparse.ArgumentParser()
    ap.add_argument("--in",           dest="in_path",       default="movie.csv",          help="Ruta a movies.csv")
    ap.add_argument("--out_xlsx",     dest="out_xlsx",      default="movie_report.xlsx",  help="Salida Excel")
    ap.add_argument("--out_clean_csv",dest="out_clean_csv", default="movie_clean.csv",    help="Salida CSV limpio")
    ap.add_argument("--out_kpis_csv", dest="out_kpis_csv",  default="movie_kpis.csv",     help="Salida CSV KPIs")
    args = ap.parse_args()  # Lee argumentos

    movies = safe_read_csv(args.in_path)           # Carga CSV de movies
    clean, kpis = clean_and_kpis_movies(movies)    # Limpia y calcula KPIs

    # Guarda Excel con dos hojas
    with pd.ExcelWriter(args.out_xlsx, engine="xlsxwriter") as xw:
        kpis.to_excel(xw, index=False, sheet_name="KPIs_movies")
        clean.to_excel(xw, index=False, sheet_name="Clean_movies")

    # Guarda CSVs separados (datos limpios + KPIs)
    clean.to_csv(args.out_clean_csv, index=False, encoding="utf-8")
    kpis.to_csv(args.out_kpis_csv,  index=False, encoding="utf-8")

    # Mensaje final en consola
    print("OK →")
    print(f"  Excel: {args.out_xlsx}")
    print(f"  CSV limpio: {args.out_clean_csv}")
    print(f"  CSV KPIs: {args.out_kpis_csv}")

if __name__ == "__main__":
    main()  # Punto de entrada
