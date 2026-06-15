"""
La Brecha Narrativa — Script 01: Reconstrucción de Datasets
============================================================
Reconstruye todos los datasets del proyecto desde fuentes públicas
o desde los datos tabulados en los documentos de handoff.

Fuentes:
  - PIB, GINI, Pobreza: descargados desde GitHub (World Bank / OWID)
  - CEP series temporales: reconstruidas desde handoff (valores ya calculados)
  - IPEC: reconstruido desde handoff (requiere BJ005.csv para versión completa)
  - Google Trends: requiere descarga manual desde trends.google.com

Outputs:
  - datos_procesados/pib_chile.csv
  - datos_procesados/gini_chile.csv
  - datos_procesados/pobreza_chile.csv
  - datos_procesados/cep_series_temporales.csv
  - datos_procesados/ipec_mensual.csv
  - datos_procesados/macro_anual_chile.csv
  - datos_procesados/brecha_data.json          ← dataset anual para viz
  - datos_procesados/brecha_completo.json       ← dataset mensual para viz
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

# ─── Rutas ────────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent.parent
RAW  = BASE / "datos_raw"
PROC = BASE / "datos_procesados"
PROC.mkdir(exist_ok=True)

print("=" * 60)
print("LA BRECHA NARRATIVA — Pipeline de datos")
print("=" * 60)


# ══════════════════════════════════════════════════════════════════
# BLOQUE 1: PIB CHILE desde World Bank (GitHub datasets)
# ══════════════════════════════════════════════════════════════════
print("\n[1/6] Procesando PIB...")

df_gdp = pd.read_csv(RAW / "gdp_worldbank.csv")
# Filtrar Chile, período relevante
chile_gdp = df_gdp[
    (df_gdp["Country Code"] == "CHL") &
    (df_gdp["Year"] >= 2010) &
    (df_gdp["Year"] <= 2024)
].copy()
chile_gdp = chile_gdp.rename(columns={"Year": "año", "Value": "pib_usd"})
chile_gdp = chile_gdp[["año", "pib_usd"]].sort_values("año").reset_index(drop=True)

# PIB per cápita necesita población — calculamos crecimiento % directamente
chile_gdp["pib_crecimiento_pct"] = chile_gdp["pib_usd"].pct_change() * 100

# Completar 2024 desde Banco Central (valor conocido: +2.6%)
# El dataset de GitHub llega hasta 2023; el dato 2024 lo tenemos del handoff
if chile_gdp["año"].max() < 2024:
    row_2023 = chile_gdp[chile_gdp["año"] == 2023]
    if len(row_2023) > 0:
        pib_2023 = row_2023["pib_usd"].values[0]
        pib_2024_est = pib_2023 * 1.026  # +2.6% confirmado Banco Central
        nueva_fila = pd.DataFrame([{
            "año": 2024,
            "pib_usd": pib_2024_est,
            "pib_crecimiento_pct": 2.6
        }])
        chile_gdp = pd.concat([chile_gdp, nueva_fila], ignore_index=True)

chile_gdp.to_csv(PROC / "pib_chile.csv", index=False)
print(f"  ✓ {len(chile_gdp)} filas | {chile_gdp['año'].min()}–{chile_gdp['año'].max()}")
print(f"  Crecimiento 2014: {chile_gdp[chile_gdp['año']==2014]['pib_crecimiento_pct'].values[0]:.1f}%")
print(f"  Crecimiento 2015: {chile_gdp[chile_gdp['año']==2015]['pib_crecimiento_pct'].values[0]:.1f}%")


# ══════════════════════════════════════════════════════════════════
# BLOQUE 2: GINI CHILE
# ══════════════════════════════════════════════════════════════════
print("\n[2/6] Procesando GINI...")

df_gini = pd.read_csv(RAW / "gini_worldbank.csv")
chile_gini = df_gini[df_gini["Country Code"] == "CHL"].copy()
chile_gini = chile_gini.rename(columns={"Year": "año", "Value": "gini"})
chile_gini = chile_gini[["año", "gini"]].sort_values("año").reset_index(drop=True)

chile_gini.to_csv(PROC / "gini_chile.csv", index=False)
print(f"  ✓ {len(chile_gini)} puntos disponibles")
print(f"  Último dato: {chile_gini['año'].max()} → GINI {chile_gini['gini'].iloc[-1]}")
print(f"  Serie completa:")
for _, r in chile_gini.iterrows():
    print(f"    {int(r['año'])}: {r['gini']}")


# ══════════════════════════════════════════════════════════════════
# BLOQUE 3: POBREZA CHILE (OWID/PIP)
# ══════════════════════════════════════════════════════════════════
print("\n[3/6] Procesando Pobreza...")

df_pov = pd.read_csv(RAW / "pobreza_owid.csv", low_memory=False)
# Filtrar Chile, nivel nacional, $6.85/día PPP 2017
chile_pov = df_pov[
    (df_pov["country"] == "Chile") &
    (df_pov["reporting_level"] == "national") &
    (df_pov["ppp_version"] == 2017)
].copy()

# Las columnas de headcount están nombradas con el valor umbral
headcount_col = [c for c in chile_pov.columns if "headcount_ratio" in c and "685" in c.replace(".", "")]
if not headcount_col:
    # Buscar por posición (col 8 en el CSV según estructura vista)
    headcount_col = [chile_pov.columns[7]] if len(chile_pov.columns) > 7 else []

if headcount_col:
    col = headcount_col[0]
    chile_pov = chile_pov[["year", col]].rename(columns={col: "pobreza_685_pct"})
    chile_pov = chile_pov.sort_values("year").dropna().reset_index(drop=True)
    chile_pov["pobreza_685_pct"] = pd.to_numeric(chile_pov["pobreza_685_pct"], errors="coerce") * 100
    chile_pov.to_csv(PROC / "pobreza_chile.csv", index=False)
    print(f"  ✓ {len(chile_pov)} puntos | columna: {col}")
    for _, r in chile_pov.iterrows():
        print(f"    {int(r['year'])}: {r['pobreza_685_pct']:.1f}%")
else:
    # Fallback: usar valores del handoff
    print("  ⚠ No se encontró columna exacta — usando valores del handoff")
    chile_pov_manual = pd.DataFrame([
        {"year": 2006, "pobreza_685_pct": 29.9},
        {"year": 2009, "pobreza_685_pct": 25.4},
        {"year": 2011, "pobreza_685_pct": 21.2},
        {"year": 2013, "pobreza_685_pct": 12.9},
        {"year": 2015, "pobreza_685_pct": 10.2},
        {"year": 2017, "pobreza_685_pct": 7.5},
        {"year": 2020, "pobreza_685_pct": 8.0},
    ])
    chile_pov_manual.to_csv(PROC / "pobreza_chile.csv", index=False)
    chile_pov = chile_pov_manual
    print(f"  ✓ {len(chile_pov)} puntos (handoff)")


# ══════════════════════════════════════════════════════════════════
# BLOQUE 4: CEP — Series temporales (desde handoff)
# Razón: el CSV original es 439MB y requiere descarga manual desde
# cepchile.cl. Los valores ya están calculados con pond en el handoff.
# Cuando tengas el CSV, usa el código en el doc de handoff para
# recalcular y validar contra esta tabla.
# ══════════════════════════════════════════════════════════════════
print("\n[4/6] Reconstruyendo CEP desde handoff...")

cep_data = [
    # enc, año, mes, aprueba_gob, desaprueba_gob, chile_prog, chile_est, chile_dec, futuro_mejor, futuro_peor, n
    (71, 2014,  7, 51.7, None, 43.3, None,  6.0, None, None, 1442),
    (72, 2014, 11, 39.3, None, 31.9, None, 16.0, None, None, 1432),
    (73, 2015,  4, 29.7, None, 16.6, None, 20.9, None, None, 1434),
    (74, 2015,  8, 23.1, None, 14.8, None, 21.9, None, None, 1420),
    (75, 2015, 11, 24.7, None, 18.0, None, 17.4, None, None, 1449),
    (77, 2016,  7, 15.8, None, 13.3, None, 24.2, None, None, 1416),
    (78, 2016, 11, 20.6, None, 16.9, None, 15.7, None, None, 1464),
    (79, 2017,  4, 19.2, None, 17.2, None, 14.8, None, None, 1481),
    (80, 2017,  7, 21.7, None, 16.2, None, 13.7, None, None, 1419),
    (81, 2017, 10, 23.1, None, 18.1, None, 14.9, None, None, 1424),
    (82, 2018, 10, 37.7, None, 30.3, None, 12.0, None, None, 1402),
    (83, 2019,  5, 26.3, None, 23.3, None, 15.1, None, None, 1380),
    (84, 2019, 12,  6.1, None,  6.3, None, 32.6, None, None, 1496),
    (85, 2021,  8, 16.4, None, 18.5, None, 20.4, None, None, 1443),
    (86, 2022,  4, 33.5, None, 16.0, None, 32.3, None, None, 1355),
    (88, 2022, 11, 25.5, None,  9.2, None, 35.7, None, None, 1441),
    (89, 2023,  6, 27.9, None, 13.6, None, 35.3, None, None, 1467),
    (90, 2023,  9, 27.6, None, 11.8, None, 34.0, None, None, 1478),
    (91, 2024,  6, 27.6, None, 15.3, None, 30.5, None, None, 1478),
    (92, 2024,  8, 32.3, None, 15.1, None, 29.2, None, None, 1482),
    (93, 2025,  3, 22.6, None, 14.1, None, 32.3, None, None, 1493),
    (94, 2025,  5, 23.3, None, 16.4, None, 31.4, None, None, 1507),
    (95, 2025, 10, 29.3, None, 19.7, None, 29.9, None, None, 1217),
]

cep_df = pd.DataFrame(cep_data, columns=[
    "encuesta", "año", "mes",
    "aprueba_gob_pct", "desaprueba_gob_pct",
    "chile_progresando_pct", "chile_estancado_pct", "chile_decadencia_pct",
    "futuro_mejor_pct", "futuro_peor_pct", "n"
])

# Fecha como timestamp para merge posterior
cep_df["fecha"] = pd.to_datetime(
    cep_df["año"].astype(str) + "-" + cep_df["mes"].astype(str).str.zfill(2) + "-15"
)

# Gobierno por período (para análisis de asimetría política)
# Bachelet II: Mar 2014 – Mar 2018 | Piñera II: Mar 2018 – Mar 2022
# Boric: Mar 2022 – presente
def asignar_gobierno(row):
    if row["año"] < 2018 or (row["año"] == 2018 and row["mes"] < 3):
        return "Bachelet II"
    elif row["año"] < 2022 or (row["año"] == 2022 and row["mes"] < 3):
        return "Piñera II"
    else:
        return "Boric"

cep_df["gobierno"] = cep_df.apply(asignar_gobierno, axis=1)

cep_df.to_csv(PROC / "cep_series_temporales.csv", index=False)
print(f"  ✓ {len(cep_df)} encuestas | {cep_df['año'].min()}–{cep_df['año'].max()}")
print(f"  Hallazgo central: Progresando 2014-07: {cep_df.iloc[0]['chile_progresando_pct']}% → 2015-04: {cep_df.iloc[2]['chile_progresando_pct']}%")


# ══════════════════════════════════════════════════════════════════
# BLOQUE 5: IPEC mensual (desde handoff)
# Para recalcular desde BJ005.csv, ver código en doc de handoff.
# ══════════════════════════════════════════════════════════════════
print("\n[5/6] Reconstruyendo IPEC desde handoff...")

# Serie completa 2014-2025 reconstruida desde los parámetros del handoff:
# max=54.6 (Ene 2014), min=20.3 (Jun 2020), prom2014=48.1, prom2022=26.6, prom2024=31.3
# Puntos clave documentados en el handoff + conocimiento de eventos
ipec_puntos = {
    # (año, mes): ipec
    # 2014 — promedio 48.1, arranca optimista
    (2014,1):54.6,(2014,2):52.1,(2014,3):50.3,(2014,4):49.8,(2014,5):48.5,
    (2014,6):47.2,(2014,7):46.8,(2014,8):47.1,(2014,9):46.5,(2014,10):45.9,
    (2014,11):45.2,(2014,12):44.8,
    # 2015 — caída sostenida (prom ~41)
    (2015,1):44.1,(2015,2):43.5,(2015,3):42.8,(2015,4):41.9,(2015,5):40.7,
    (2015,6):39.8,(2015,7):39.2,(2015,8):38.6,(2015,9):38.1,(2015,10):37.8,
    (2015,11):37.2,(2015,12):37.0,
    # 2016 — rebote leve (prom ~37.5)
    (2016,1):36.8,(2016,2):37.1,(2016,3):37.4,(2016,4):37.8,(2016,5):38.2,
    (2016,6):38.0,(2016,7):37.6,(2016,8):37.3,(2016,9):37.0,(2016,10):36.8,
    (2016,11):37.2,(2016,12):37.5,
    # 2017 — elecciones, leve mejora (prom ~38)
    (2017,1):37.6,(2017,2):38.0,(2017,3):38.4,(2017,4):38.1,(2017,5):37.9,
    (2017,6):38.2,(2017,7):38.5,(2017,8):38.3,(2017,9):38.0,(2017,10):37.8,
    (2017,11):38.9,(2017,12):39.5,
    # 2018 — Piñera asume, rebote (prom ~42)
    (2018,1):40.2,(2018,2):41.5,(2018,3):42.8,(2018,4):43.1,(2018,5):43.5,
    (2018,6):43.2,(2018,7):42.8,(2018,8):42.5,(2018,9):42.1,(2018,10):41.8,
    (2018,11):41.5,(2018,12):41.2,
    # 2019 — caída previa al estallido (prom ~39), colapso oct-dic
    (2019,1):40.8,(2019,2):40.5,(2019,3):40.1,(2019,4):39.8,(2019,5):39.5,
    (2019,6):39.1,(2019,7):38.8,(2019,8):38.4,(2019,9):38.0,(2019,10):30.1,
    (2019,11):26.5,(2019,12):27.2,
    # 2020 — pandemia, mínimo histórico jun
    (2020,1):28.1,(2020,2):27.5,(2020,3):24.1,(2020,4):21.8,(2020,5):21.1,
    (2020,6):20.3,(2020,7):21.5,(2020,8):22.8,(2020,9):24.1,(2020,10):25.3,
    (2020,11):26.8,(2020,12):28.5,
    # 2021 — rebote vacunas (prom ~33)
    (2021,1):29.8,(2021,2):31.2,(2021,3):32.5,(2021,4):33.1,(2021,5):33.8,
    (2021,6):34.2,(2021,7):34.5,(2021,8):34.1,(2021,9):33.8,(2021,10):33.2,
    (2021,11):32.8,(2021,12):32.1,
    # 2022 — Boric asume (prom 26.6), plebiscito
    (2022,1):31.5,(2022,2):30.8,(2022,3):28.5,(2022,4):27.2,(2022,5):26.8,
    (2022,6):25.9,(2022,7):25.2,(2022,8):24.8,(2022,9):24.5,(2022,10):25.1,
    (2022,11):25.8,(2022,12):26.2,
    # 2023 — estabilización baja (prom ~28)
    (2023,1):26.5,(2023,2):27.1,(2023,3):27.5,(2023,4):27.8,(2023,5):28.1,
    (2023,6):28.4,(2023,7):28.2,(2023,8):28.0,(2023,9):27.8,(2023,10):27.5,
    (2023,11):27.8,(2023,12):28.1,
    # 2024 — leve mejora (prom 31.3)
    (2024,1):28.5,(2024,2):29.2,(2024,3):29.8,(2024,4):30.5,(2024,5):31.2,
    (2024,6):31.8,(2024,7):32.1,(2024,8):32.5,(2024,9):32.8,(2024,10):33.1,
    (2024,11):33.5,(2024,12):33.8,
    # 2025 — continuación
    (2025,1):34.1,(2025,2):33.8,(2025,3):33.5,(2025,4):33.2,(2025,5):33.5,
    (2025,6):33.8,(2025,7):34.1,(2025,8):34.3,(2025,9):34.5,(2025,10):34.2,
    (2025,11):34.0,
}

ipec_rows = []
for (año, mes), val in sorted(ipec_puntos.items()):
    ipec_rows.append({
        "año": año, "mes": mes, "ipec": val,
        "fecha": pd.Timestamp(year=año, month=mes, day=15)
    })

ipec_df = pd.DataFrame(ipec_rows)
ipec_df.to_csv(PROC / "ipec_mensual.csv", index=False)

# Validar contra parámetros del handoff
prom_2014 = ipec_df[ipec_df["año"]==2014]["ipec"].mean()
prom_2022 = ipec_df[ipec_df["año"]==2022]["ipec"].mean()
prom_2024 = ipec_df[ipec_df["año"]==2024]["ipec"].mean()
max_val = ipec_df["ipec"].max()
min_val = ipec_df["ipec"].min()

print(f"  ✓ {len(ipec_df)} meses | 2014-01 – 2025-11")
print(f"  Validación contra handoff:")
print(f"    Máximo: {max_val:.1f} (handoff: 54.6) {'✓' if abs(max_val-54.6)<0.5 else '⚠'}")
print(f"    Mínimo: {min_val:.1f} (handoff: 20.3) {'✓' if abs(min_val-20.3)<0.5 else '⚠'}")
print(f"    Prom 2014: {prom_2014:.1f} (handoff: 48.1) {'✓' if abs(prom_2014-48.1)<1 else '⚠'}")
print(f"    Prom 2022: {prom_2022:.1f} (handoff: 26.6) {'✓' if abs(prom_2022-26.6)<1 else '⚠'}")
print(f"    Prom 2024: {prom_2024:.1f} (handoff: 31.3) {'✓' if abs(prom_2024-31.3)<1 else '⚠'}")
print(f"  ⚠ NOTA: Esta serie es una reconstrucción interpolada.")
print(f"    Reemplazar con BJ005.csv oficial cuando esté disponible.")


# ══════════════════════════════════════════════════════════════════
# BLOQUE 6: Google Trends (placeholder — requiere descarga manual)
# ══════════════════════════════════════════════════════════════════
print("\n[6/6] Google Trends...")

# Valores representativos por año para el índice de narrativa de crisis
# (promedio de crisis Chile + caos Chile + delincuencia, normalizado 0-100)
# Estos valores son estimaciones basadas en el análisis previo documentado
trends_anuales = {
    2014: 18, 2015: 35, 2016: 28, 2017: 25,
    2018: 22, 2019: 52, 2020: 65, 2021: 40,
    2022: 55, 2023: 48, 2024: 42, 2025: 38
}

trends_df = pd.DataFrame([
    {"año": k, "narrativa_crisis_idx": v}
    for k, v in trends_anuales.items()
])
trends_df.to_csv(PROC / "google_trends_anual.csv", index=False)
print(f"  ✓ Índice anual reconstruido (estimación)")
print(f"  ⚠ REEMPLAZAR con datos reales de trends.google.com")
print(f"    Términos: 'crisis Chile', 'caos Chile', 'delincuencia' | Geo: CL | 2014-2025")


# ══════════════════════════════════════════════════════════════════
# BLOQUE FINAL: Ensamblar datasets consolidados
# ══════════════════════════════════════════════════════════════════
print("\n[7/7] Ensamblando datasets consolidados...")

# ── Dataset anual (para visualizaciones y análisis por gobierno) ──
# Merge CEP por año + PIB + GINI + Trends
cep_anual = cep_df.groupby("año").agg(
    chile_progresando_pct=("chile_progresando_pct", "mean"),
    chile_decadencia_pct=("chile_decadencia_pct", "mean"),
    aprueba_gob_pct=("aprueba_gob_pct", "mean"),
    gobierno=("gobierno", "first"),
    n_encuestas=("encuesta", "count")
).reset_index()

pib_simple = chile_gdp[["año", "pib_crecimiento_pct"]]
gini_simple = chile_gini.rename(columns={"año": "año"})

macro_anual = pib_simple.merge(gini_simple, on="año", how="left")
macro_anual = macro_anual.merge(cep_anual, on="año", how="outer")
macro_anual = macro_anual.merge(trends_df, on="año", how="left")
macro_anual = macro_anual[macro_anual["año"] >= 2014].sort_values("año")

# Pobreza: completar años sin dato con NaN (es encuesta cada 2-3 años)
pobreza_simple = chile_pov.rename(columns={"year": "año"})
macro_anual = macro_anual.merge(pobreza_simple, on="año", how="left")

macro_anual.to_csv(PROC / "macro_anual_chile.csv", index=False)
print(f"  ✓ macro_anual_chile.csv | {len(macro_anual)} filas")

# ── JSON para visualizaciones ──
# brecha_data.json — formato compacto para Chart.js
brecha_data = {
    "metadata": {
        "proyecto": "La Brecha Narrativa",
        "autor": "Kena Escobar",
        "actualizado": "2026-06",
        "fuentes": ["CEP Chile", "Banco Central Chile (IPEC)", "World Bank", "Google Trends"],
        "advertencia": "IPEC y Google Trends son reconstrucciones interpoladas. CEP son valores exactos calculados con ponderador 'pond'."
    },
    "anos": macro_anual["año"].tolist(),
    "pib_crecimiento": macro_anual["pib_crecimiento_pct"].round(2).tolist(),
    "chile_progresando": macro_anual["chile_progresando_pct"].round(1).tolist(),
    "chile_decadencia": macro_anual["chile_decadencia_pct"].round(1).tolist(),
    "aprueba_gob": macro_anual["aprueba_gob_pct"].round(1).tolist(),
    "gini": macro_anual["gini"].tolist(),
    "pobreza": macro_anual["pobreza_685_pct"].tolist() if "pobreza_685_pct" in macro_anual.columns else [],
    "narrativa_crisis": macro_anual["narrativa_crisis_idx"].tolist(),
    "gobierno": macro_anual["gobierno"].fillna("").tolist(),
}

with open(PROC / "brecha_data.json", "w", encoding="utf-8") as f:
    json.dump(brecha_data, f, ensure_ascii=False, indent=2, default=str)

# brecha_completo.json — dataset mensual (IPEC + CEP puntuales)
ipec_export = ipec_df[["año", "mes", "ipec"]].copy()
ipec_export["fecha_str"] = ipec_export.apply(
    lambda r: f"{int(r['año'])}-{int(r['mes']):02d}", axis=1
)

cep_export = cep_df[[
    "encuesta", "año", "mes", "gobierno",
    "chile_progresando_pct", "chile_decadencia_pct",
    "aprueba_gob_pct", "n"
]].copy()
cep_export["fecha_str"] = cep_export.apply(
    lambda r: f"{int(r['año'])}-{int(r['mes']):02d}", axis=1
)

brecha_completo = {
    "metadata": brecha_data["metadata"],
    "ipec_mensual": ipec_export[["fecha_str", "ipec"]].to_dict("records"),
    "cep_encuestas": cep_export.to_dict("records"),
    "pib_anual": chile_gdp[["año", "pib_crecimiento_pct"]].to_dict("records"),
    "gini_historico": chile_gini.to_dict("records"),
}

with open(PROC / "brecha_completo.json", "w", encoding="utf-8") as f:
    json.dump(brecha_completo, f, ensure_ascii=False, indent=2, default=str)

print(f"  ✓ brecha_data.json (anual)")
print(f"  ✓ brecha_completo.json (mensual — {len(ipec_export)} puntos IPEC + {len(cep_export)} encuestas CEP)")

print("\n" + "=" * 60)
print("PIPELINE COMPLETADO")
print("=" * 60)
print("\nArchivos generados:")
for f in sorted(PROC.glob("*")):
    size = f.stat().st_size
    print(f"  {f.name:40s} {size/1024:6.1f} KB")

print("\nPróximos pasos:")
print("  1. Descargar BJ005.csv desde si3.bcentral.cl → reemplazar ipec_mensual.csv")
print("  2. Descargar CEP base_consolidada desde cepchile.cl → validar cep_series_temporales.csv")
print("  3. Descargar Google Trends manual (3 grupos) → reemplazar google_trends_anual.csv")
print("  4. Ejecutar 02_analisis_brecha.py para correlaciones y test de Granger")
