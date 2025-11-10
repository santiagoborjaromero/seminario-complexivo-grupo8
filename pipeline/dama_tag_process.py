
# -*- coding: utf-8 -*-
"""
tags_clean_kpis_commented.py
Limpia tags.csv, calcula KPIs (DAMA) y guarda:
 - Excel: tags_report.xlsx (hojas: KPIs_tags, Clean_tags)
 - CSV:   tags_clean.csv, tags_kpis.csv
Uso:
  python tags_clean_kpis_commented.py --in tags.csv --movies movies.csv --out_xlsx tags_report.xlsx --out_clean_csv tags_clean.csv --out_kpis_csv tags_kpis.csv
"""
import pandas as pd  # Manipulación de datos
import numpy as np   # Utilidades numéricas
import argparse      # Argumentos CLI


#NOW = pd.Timestamp.utcnow()

def pct(ok, total):
    """Porcentaje con redondeo a 2 decimales y protección de división por cero."""
    return float(round(100.0 * (ok / total if total else 0), 2))

def kpi_row(name, val, total, target=None, note=""):
    """Estructura estándar para una fila KPI de tags."""
    return {"Tabla": "tags", "KPI": name, "Valor_%": val, "Total_registros": total, "Meta_%": target, "Notas": note}

def safe_read_csv(path):
    """Lectura de CSV con soporte para ',' o ';'."""
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.read_csv(path, sep=';')

def parse_timestamp(series: pd.Series):
    """Convierte a datetime manejando epoch y strings dd/mm/YYYY HH:MM."""
    s = series.copy()                                                    # Copia de la serie
    is_epoch_like = s.astype(str).str.fullmatch(r"\d+(\.\d+)?", na=False)# Detecta números
    s_epoch = pd.to_numeric(s.where(is_epoch_like), errors="coerce")     # A numérico
    dt_epoch = pd.to_datetime(s_epoch, unit="s", errors="coerce")        # Epoch → datetime
    dt_dmy = pd.to_datetime(s, format="%d/%m/%Y %H:%M", errors="coerce") # dd/mm/YYYY HH:MM
    dt_auto = pd.to_datetime(s, errors="coerce", dayfirst=True)          # Genérico dayfirst
    return dt_epoch.fillna(dt_dmy).fillna(dt_auto)                       # Prioridad: epoch > dmy > auto

def clean_and_kpis_tags(df_tags: pd.DataFrame, movies_ids: pd.Series | None):
    """Limpia y calcula KPIs sobre tags. Valida FK contra movies si se provee."""
    df = df_tags.copy()                                # Copia
    cols = {c.lower(): c for c in df.columns}          # Mapa de columnas
    userId    = cols.get("userid", "userId" if "userId" in df.columns else df.columns[0])   # userId detectado
    movieId   = cols.get("movieid", "movieId" if "movieId" in df.columns else df.columns[1])# movieId detectado
    tag       = cols.get("tag", "tag")                 # tag detectado
    timestamp = cols.get("timestamp", "timestamp")     # timestamp detectado

    df[userId]  = pd.to_numeric(df[userId], errors="coerce")  # userId → numérico
    df[movieId] = pd.to_numeric(df[movieId], errors="coerce") # movieId → numérico
    df[tag]     = df[tag].astype(str).str.strip()             # tag → str y sin espacios sobrantes
    df["_dt"]   = parse_timestamp(df[timestamp])              # parseo de fecha

    n = len(df)                        # Total de filas
    kpis = []                          # KPIs acumulados

    # Completitud/validez básica de IDs y tag
    kpis.append(kpi_row("% userId no nulos", pct(df[userId].notna().sum(), n), n, 100))
    kpis.append(kpi_row("% movieId no nulos", pct(df[movieId].notna().sum(), n), n, 100))
    kpis.append(kpi_row("% tag no vacío", pct((df[tag].str.len() > 0).sum(), n), n, 95))

    # Integridad referencial contra movies (si existe catálogo)
    if movies_ids is not None and len(movies_ids) > 0:
        fk_ok = df[movieId].isin(set(pd.to_numeric(movies_ids, errors="coerce").dropna().astype(int)))
        kpis.append(kpi_row("% FK movieId en movies", pct(fk_ok.sum(), n), n, 99))
    else:
        fk_ok = pd.Series([True]*n, index=df.index)  # Sin catálogo, no penaliza

    # Validez/razonabilidad de timestamp
    # 1) Normaliza la columna a datetime y quita zona horaria (queda datetime64[ns] "naive")
    df["_dt"] = pd.to_datetime(df["_dt"], errors="coerce", utc=True).dt.tz_convert(None)

    # 2) Asegura que NOW también sea naive (UTC sin tz)
    NOW = pd.Timestamp.utcnow().tz_localize(None)

    # 3) Ahora sí: valida y compara sin error
    dt_valid = df["_dt"].notna()
    dt_not_future = dt_valid & (df["_dt"] <= NOW)

    kpis.append(kpi_row("% timestamps válidos", pct(dt_valid.sum(), n), n, 98))
    kpis.append(kpi_row("% timestamps no futuros", pct((dt_valid & dt_not_future).sum(), n), n, 98))

    # Razonabilidad simple del tag (longitud/formato)
    tag_reasonable = df[tag].str.len().between(1, 100) & df[tag].str.fullmatch(r"[^\s].*", na=False)
    kpis.append(kpi_row("% tags razonables", pct(tag_reasonable.sum(), n), n, 95))

    # --- Limpieza ---
    keep = (
        df[userId].notna()          # userId válido
        & df[movieId].notna()       # movieId válido
        & (df[tag].str.len() > 0)   # tag no vacío
        & dt_valid & dt_not_future  # fecha válida y no futura
        & fk_ok                     # FK válida (si aplica)
        & tag_reasonable            # tag razonable
    )
    df_clean = df.loc[keep].copy()           # Filtra registros válidos
    df_clean = df_clean.drop(columns=["_dt"])# Quita auxiliar

    # Deduplicación: si (userId, movieId, tag) se repite, conservar el más reciente
    df_clean["_dt"] = parse_timestamp(df_clean[timestamp])                          # Recalcula datetime
    df_clean = df_clean.sort_values("_dt").drop_duplicates(subset=[userId, movieId, tag], keep="last")  # Deja último
    df_clean = df_clean.drop(columns=["_dt"])                                       # Quita auxiliar

    kpi_df = pd.DataFrame(kpis)   # KPIs en DataFrame
    return df_clean, kpi_df       # Devuelve limpios + KPIs

def main():
    # Argumentos de entrada/salida
    ap = argparse.ArgumentParser()
    ap.add_argument("--in",           dest="in_path",      default="tag.csv",           help="Ruta a tags.csv")
    ap.add_argument("--movies",       dest="movies_path",  default=None,                 help="Ruta a movies.csv (opcional) para validar FK")
    ap.add_argument("--out_xlsx",     dest="out_xlsx",     default="tag_report.xlsx",   help="Salida Excel")
    ap.add_argument("--out_clean_csv",dest="out_clean_csv",default="tag_clean.csv",     help="Salida CSV limpio")
    ap.add_argument("--out_kpis_csv", dest="out_kpis_csv", default="tag_kpis.csv",      help="Salida CSV KPIs")
    args = ap.parse_args()  # Lee argumentos

    tags = safe_read_csv(args.in_path)  # Carga tags
    movies_ids = None                   # Inicializa catálogo
    if args.movies_path:                # Si se provee ruta a movies
        movies = safe_read_csv(args.movies_path)     # Carga movies
        mcols = {c.lower(): c for c in movies.columns}  # Mapa de columnas
        movieId_col = mcols.get("movieid", "movieId" if "movieId" in movies.columns else movies.columns[0]) # Detecta columna
        movies_ids = movies[movieId_col]             # Serie con IDs

    clean, kpis = clean_and_kpis_tags(tags, movies_ids)  # Limpia y calcula KPIs

    # Guarda Excel con dos hojas
    with pd.ExcelWriter(args.out_xlsx, engine="xlsxwriter") as xw:
        kpis.to_excel(xw, index=False, sheet_name="KPIs_tags")
        clean.to_excel(xw, index=False, sheet_name="Clean_tags")

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
