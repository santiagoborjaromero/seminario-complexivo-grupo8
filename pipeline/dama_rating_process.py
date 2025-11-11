
import pandas as pd  # Manipulación de datos
import numpy as np   # Operaciones numéricas
import argparse      # Argumentos CLI


#NOW = pd.Timestamp.utcnow()  # Marca temporal actual (UTC)

def pct(ok, total):
    """Calcula porcentaje con 2 decimales."""
    return float(round(100.0 * (ok / total if total else 0), 2))

def kpi_row(name, val, total, target=None, note=""):
    """Crea estructura estándar de KPI para ratings."""
    return {"Tabla": "ratings", "KPI": name, "Valor_%": val, "Total_registros": total, "Meta_%": target, "Notas": note}

def safe_read_csv(path):
    """Lee CSV tolerando coma o punto y coma."""
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.read_csv(path, sep=';')

def parse_timestamp(series: pd.Series):
    """Parsea timestamps que pueden ser epoch o strings (dd/mm/YYYY HH:MM)."""
    s = series.copy()                                                    # Copia para no mutar original
    is_epoch_like = s.astype(str).str.fullmatch(r"\d+(\.\d+)?", na=False) # Detecta números enteros/float
    s_epoch = pd.to_numeric(s.where(is_epoch_like), errors="coerce")      # Convierte posibles epoch a numérico
    dt_epoch = pd.to_datetime(s_epoch, unit="s", errors="coerce")         # Epoch → datetime
    dt_dmy = pd.to_datetime(s, format="%d/%m/%Y %H:%M", errors="coerce")  # Intento con dd/mm/YYYY HH:MM
    dt_auto = pd.to_datetime(s, errors="coerce", dayfirst=True)           # Intento genérico con dayfirst
    return dt_epoch.fillna(dt_dmy).fillna(dt_auto)                        # Prioriza epoch, luego dmy, luego auto

def clean_and_kpis_ratings(df_ratings: pd.DataFrame, movies_ids: pd.Series | None):
    """Limpia y calcula KPIs sobre ratings. Valida FK contra movies si se provee."""
    df = df_ratings.copy()                               # Copia de trabajo
    cols = {c.lower(): c for c in df.columns}            # Mapa de nombres
    userId    = cols.get("userid", "userId" if "userId" in df.columns else df.columns[0])   # userId detectado
    movieId   = cols.get("movieid", "movieId" if "movieId" in df.columns else df.columns[1])# movieId detectado
    rating    = cols.get("rating", "rating")             # rating detectado
    timestamp = cols.get("timestamp", "timestamp")       # timestamp detectado

    df[userId]  = pd.to_numeric(df[userId], errors="coerce")     # userId a numérico
    df[movieId] = pd.to_numeric(df[movieId], errors="coerce")    # movieId a numérico
    df[rating]  = pd.to_numeric(df[rating], errors="coerce")     # rating a numérico
    df["_dt"]   = parse_timestamp(df[timestamp])                 # parsea timestamp

    n = len(df)                                      # Total registros
    kpis = []                                        # Lista de KPIs

    # Integridad básica de IDs
    kpis.append(kpi_row("% userId válidos", pct(df[userId].notna().sum(), n), n, 100))
    kpis.append(kpi_row("% movieId válidos", pct(df[movieId].notna().sum(), n), n, 100))

    # Integridad referencial contra movies (si se dispone)
    if movies_ids is not None and len(movies_ids) > 0:
        fk_ok = df[movieId].isin(set(pd.to_numeric(movies_ids, errors="coerce").dropna().astype(int)))
        kpis.append(kpi_row("% FK movieId en movies", pct(fk_ok.sum(), n), n, 99))
    else:
        fk_ok = pd.Series([True]*n, index=df.index)  # Si no hay catálogo, no penaliza

    # Razonabilidad de rating en 0..5
    rating_range_ok = df[rating].between(0, 5, inclusive="both")
    kpis.append(kpi_row("% ratings 0..5", pct(rating_range_ok.fillna(False).sum(), n), n, 99))

    # Validez: numérico (no NaN)
    kpis.append(kpi_row("% ratings numéricos", pct(df[rating].notna().sum(), n), n, 99))

    # Validez/razonabilidad de fechas
   # 1) Normaliza la columna a datetime y quita zona horaria (queda datetime64[ns] "naive")
    df["_dt"] = pd.to_datetime(df["_dt"], errors="coerce", utc=True).dt.tz_convert(None)

    # 2) Asegura que NOW también sea naive (UTC sin tz)
    NOW = pd.Timestamp.utcnow().tz_localize(None)

    # 3) Ahora sí: valida y compara sin error
    dt_valid = df["_dt"].notna()
    dt_not_future = dt_valid & (df["_dt"] <= NOW)
    kpis.append(kpi_row("% timestamps válidos", pct(dt_valid.sum(), n), n, 98))
    kpis.append(kpi_row("% timestamps no futuros", pct((dt_valid & dt_not_future).sum(), n), n, 98))

    # Consistencia: (userId, movieId) no debería tener múltiples ratings distintos
    dup_pair = df.duplicated(subset=[userId, movieId], keep=False)  # Detecta pares repetidos
    consistent_pairs = pd.Series(True, index=df.index)              # Asume consistentes
    if dup_pair.any():                                              # Si hay duplicados del par
        grp = df.groupby([userId, movieId])[rating].nunique()       # Cuenta ratings distintos por par
        bad_pairs = set(grp[grp > 1].index)                         # Pares con más de un valor
        if bad_pairs:                                               # Si existen
            inconsistent_mask = df.set_index([userId, movieId]).index.isin(bad_pairs)  # Marca inconsistentes
            consistent_pairs = ~pd.Series(inconsistent_mask, index=df.index)            # Inversa (consistentes)

    kpis.append(kpi_row("% pares (userId,movieId) consistentes", pct(consistent_pairs.sum(), n), n, 99))

    # --- Limpieza ---
    keep = (
        df[userId].notna()            # userId válido
        & df[movieId].notna()         # movieId válido
        & rating_range_ok             # rating en rango
        & dt_valid & dt_not_future    # fecha válida y no futura
        & fk_ok                       # FK válida (si aplica)
    )
    df_clean = df.loc[keep].copy()                                        # Filtra
    df_clean = df_clean.sort_values("_dt").drop_duplicates(subset=[userId, movieId], keep="last")  # Dejar último rating por par
    df_clean = df_clean.drop(columns=["_dt"])                             # Quita auxiliar

    kpi_df = pd.DataFrame(kpis)         # KPIs en DataFrame
    return df_clean, kpi_df             # Devuelve limpios + KPIs

def main():
    # Argumentos: entrada ratings, catálogo movies opcional, y salidas
    ap = argparse.ArgumentParser()
    ap.add_argument("--in",           dest="in_path",      default="rating.csv",           help="Ruta a ratings.csv")
    ap.add_argument("--movies",       dest="movies_path",  default=None,                    help="Ruta a movies.csv para validar FK (opcional)")
    ap.add_argument("--out_xlsx",     dest="out_xlsx",     default="rating_report.xlsx",   help="Salida Excel")
    ap.add_argument("--out_clean_csv",dest="out_clean_csv",default="rating_clean.csv",     help="Salida CSV limpio")
    ap.add_argument("--out_kpis_csv", dest="out_kpis_csv", default="rating_kpis.csv",      help="Salida CSV KPIs")
    args = ap.parse_args()  # Lee argumentos

    ratings = safe_read_csv(args.in_path)   # Carga ratings
    movies_ids = None                       # Inicializa catálogo de películas
    if args.movies_path:                    # Si se proporciona ruta a movies
        movies = safe_read_csv(args.movies_path)   # Carga movies
        mcols = {c.lower(): c for c in movies.columns}         # Mapa de columnas
        movieId_col = mcols.get("movieid", "movieId" if "movieId" in movies.columns else movies.columns[0])  # Detecta nombre
        movies_ids = movies[movieId_col]   # Serie con los IDs

    clean, kpis = clean_and_kpis_ratings(ratings, movies_ids)  # Limpia/calcula KPIs

    # Guarda Excel con dos hojas
    with pd.ExcelWriter(args.out_xlsx, engine="xlsxwriter") as xw:
        kpis.to_excel(xw, index=False, sheet_name="KPIs_ratings")
    #     clean.to_excel(xw, index=False, sheet_name="Clean_ratings")

    # Guarda CSVs separados (datos limpios + KPIs)
    clean.to_csv(args.out_clean_csv, index=False, encoding="utf-8")
    kpis.to_csv(args.out_kpis_csv,  index=False, encoding="utf-8")

    # Mensaje final
    print("OK →")
    print(f"  Excel: {args.out_xlsx}")
    print(f"  CSV limpio: {args.out_clean_csv}")
    print(f"  CSV KPIs: {args.out_kpis_csv}")

if __name__ == "__main__":
    main()  # Ejecuta
