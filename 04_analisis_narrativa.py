"""
La Brecha Narrativa — Script 04: Análisis de Narrativa vs Percepción
=====================================================================
Valida la hipótesis central con titulares reales de medios (Emol + La Tercera)
en lugar del proxy Google Trends usado en la Fase 1.

HIPÓTESIS: La narrativa mediática de crisis PRECEDE a la caída del IPEC
           (percepción ciudadana) con un lag de ~6 meses.

INPUTS:
  datos_procesados/titulares_raw.csv     ← output de 03_scraping_titulares.py
  brecha_completo.json                   ← IPEC mensual + Google Trends

OUTPUTS:
  datos_procesados/narrativa_vs_ipec.csv     ← serie mensual fusionada
  datos_procesados/resultados_granger.json   ← test estadístico
  datos_procesados/04_resultados.txt         ← resumen legible

ANÁLISIS:
  1. Agrega titulares por mes → ratio_crisis (0–1)
  2. Merge con IPEC mensual
  3. Correlación cruzada (CCF) con lags 0 a 12 meses
  4. Test de Granger: ¿titulares → IPEC? ¿con qué lag?
  5. Comparación con Google Trends como proxy
"""

import json
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

warnings.filterwarnings('ignore')

# ─── Rutas ────────────────────────────────────────────────────────────────────
BASE         = Path(__file__).parent
PROC         = BASE / "datos_procesados"
CSV_TITULARES = PROC / "titulares_raw.csv"
JSON_COMPLETO = BASE / "brecha_completo.json"
OUT_SERIE    = PROC / "narrativa_vs_ipec.csv"
OUT_GRANGER  = PROC / "resultados_granger.json"
OUT_RESUMEN  = PROC / "04_resultados.txt"

print("=" * 65)
print("LA BRECHA NARRATIVA — Análisis Narrativa vs Percepción")
print("=" * 65)


# ══════════════════════════════════════════════════════════════════
# BLOQUE 1: Cargar y validar titulares
# ══════════════════════════════════════════════════════════════════
print("\n[1/5] Cargando titulares...")

if not CSV_TITULARES.exists():
    print(f"  ✗ No se encontró {CSV_TITULARES}")
    print(f"    Ejecuta primero: python3 03_scraping_titulares.py")
    exit(1)

df_tit = pd.read_csv(CSV_TITULARES, encoding='utf-8')
df_tit['fecha'] = pd.to_datetime(df_tit['fecha'])

print(f"  ✓ {len(df_tit)} titulares cargados")
print(f"  Período: {df_tit['fecha'].min().strftime('%Y-%m')} – "
      f"{df_tit['fecha'].max().strftime('%Y-%m')}")
print(f"  Medios: {df_tit['medio'].value_counts().to_dict()}")
print(f"  Tono:")
for tono, n in df_tit['tono_estimado'].value_counts().items():
    print(f"    {tono:<10} {n:5d}  ({n/len(df_tit)*100:.1f}%)")


# ══════════════════════════════════════════════════════════════════
# BLOQUE 2: Agregar por mes → índice de narrativa de crisis
# ══════════════════════════════════════════════════════════════════
print("\n[2/5] Agregando por mes...")

# ratio_crisis = titulares_crisis / total_titulares del mes
# Usar todos los medios combinados para máxima señal
df_tit['año_mes'] = df_tit['fecha'].dt.to_period('M')

mensual = (
    df_tit
    .groupby('año_mes')
    .agg(
        total_titulares   = ('titular', 'count'),
        n_crisis          = ('tono_estimado', lambda x: (x == 'crisis').sum()),
        n_positivo        = ('tono_estimado', lambda x: (x == 'positivo').sum()),
        n_neutro          = ('tono_estimado', lambda x: (x == 'neutro').sum()),
    )
    .reset_index()
)
mensual['ratio_crisis']   = mensual['n_crisis']   / mensual['total_titulares']
mensual['ratio_positivo'] = mensual['n_positivo'] / mensual['total_titulares']
mensual['fecha']          = mensual['año_mes'].dt.to_timestamp()
mensual['año']            = mensual['fecha'].dt.year
mensual['mes']            = mensual['fecha'].dt.month

print(f"  ✓ {len(mensual)} meses con datos de titulares")
print(f"  ratio_crisis promedio: {mensual['ratio_crisis'].mean():.3f}")
print(f"  ratio_crisis máximo : {mensual['ratio_crisis'].max():.3f} "
      f"({mensual.loc[mensual['ratio_crisis'].idxmax(), 'año_mes']})")

# También calcular por medio separado para comparar Emol vs La Tercera
mensual_medio = (
    df_tit
    .groupby(['año_mes', 'medio'])
    .agg(
        total=('titular','count'),
        n_crisis=('tono_estimado', lambda x: (x=='crisis').sum()),
    )
    .reset_index()
)
mensual_medio['ratio_crisis'] = mensual_medio['n_crisis'] / mensual_medio['total']


# ══════════════════════════════════════════════════════════════════
# BLOQUE 3: Merge con IPEC y Google Trends
# ══════════════════════════════════════════════════════════════════
print("\n[3/5] Mergeando con IPEC y Google Trends...")

with open(JSON_COMPLETO, encoding='utf-8') as f:
    completo = json.load(f)

df_ipec = pd.DataFrame(completo['trends_ipec_mensual'])
df_ipec['fecha'] = pd.to_datetime(df_ipec['fecha'])
df_ipec['año_mes'] = df_ipec['fecha'].dt.to_period('M')

# Merge: titulares ← IPEC + Trends
df = mensual.merge(
    df_ipec[['año_mes','ipec','narrativa_crisis_idx','delincuencia']],
    on='año_mes', how='inner'
)

print(f"  ✓ {len(df)} meses con datos completos (titulares + IPEC + Trends)")
print(f"  Período efectivo: {df['año_mes'].min()} – {df['año_mes'].max()}")
print(f"  Filas sin IPEC: {df['ipec'].isna().sum()}")

df = df.sort_values('fecha').reset_index(drop=True)
df.to_csv(OUT_SERIE, index=False, encoding='utf-8')
print(f"  Guardado: {OUT_SERIE}")


# ══════════════════════════════════════════════════════════════════
# BLOQUE 4: Correlación cruzada (CCF) con lags 0–12
# ══════════════════════════════════════════════════════════════════
print("\n[4/5] Correlación cruzada (lag 0–12 meses)...")

def ccf_serie(x: pd.Series, y: pd.Series, max_lag: int = 12) -> dict:
    """
    Correlación cruzada entre x (t) e y (t + lag).
    Lag positivo: x precede a y.
    Devuelve lag de correlación máxima en valor absoluto.
    """
    x_std = (x - x.mean()) / x.std()
    y_std = (y - y.mean()) / y.std()
    correlaciones = {}
    for lag in range(0, max_lag + 1):
        if lag == 0:
            r, p = stats.pearsonr(x_std, y_std)
        else:
            r, p = stats.pearsonr(x_std.iloc[:-lag], y_std.iloc[lag:])
        correlaciones[lag] = {'r': round(r, 4), 'p': round(p, 4)}
    # Lag con correlación máxima (absoluta)
    best_lag = max(correlaciones, key=lambda l: abs(correlaciones[l]['r']))
    return {'por_lag': correlaciones, 'mejor_lag': best_lag,
            'r_mejor': correlaciones[best_lag]['r'],
            'p_mejor': correlaciones[best_lag]['p']}

# Comparar tres proxies de narrativa contra IPEC
proxies = {
    'titulares_ratio_crisis': df['ratio_crisis'],
    'google_trends_narrativa': df['narrativa_crisis_idx'],
    'google_trends_delincuencia': df['delincuencia'],
}

resultados_ccf = {}
print(f"\n  {'Proxy':<32} {'Mejor lag':>10} {'r':>8} {'p':>8} {'Significativo':>14}")
print(f"  {'─'*32} {'─'*10} {'─'*8} {'─'*8} {'─'*14}")

for nombre, serie in proxies.items():
    # Solo usar filas sin NaN
    mask  = serie.notna() & df['ipec'].notna()
    res   = ccf_serie(serie[mask], df['ipec'][mask])
    sig   = "✓ p<0.05" if res['p_mejor'] < 0.05 else "✗ n.s."
    print(f"  {nombre:<32} {res['mejor_lag']:>9} m  {res['r_mejor']:>+7.4f}  "
          f"{res['p_mejor']:>7.4f}  {sig:>14}")
    resultados_ccf[nombre] = res

# Mostrar perfil completo de CCF para titulares
print(f"\n  Perfil CCF completo — titulares_ratio_crisis → IPEC:")
print(f"  {'Lag':>5}   {'r':>8}   {'p':>8}   {'Sig':>6}")
for lag, vals in resultados_ccf['titulares_ratio_crisis']['por_lag'].items():
    sig = "*" if vals['p'] < 0.05 else ""
    bar = "█" * int(abs(vals['r']) * 20)
    print(f"  {lag:>4}m   {vals['r']:>+7.4f}   {vals['p']:>7.4f}   {sig:>4}  {bar}")


# ══════════════════════════════════════════════════════════════════
# BLOQUE 5: Test de Granger
# ══════════════════════════════════════════════════════════════════
print("\n[5/5] Test de causalidad de Granger...")

try:
    from statsmodels.tsa.stattools import grangercausalitytests, adfuller
    STATSMODELS = True
except ImportError:
    STATSMODELS = False
    print("  ⚠ statsmodels no instalado — omitiendo test formal de Granger")
    print("    Instalar con: pip3 install statsmodels")

resultados_granger = {}

if STATSMODELS:
    def test_estacionariedad(serie: pd.Series, nombre: str) -> bool:
        """ADF test — retorna True si la serie es estacionaria (p < 0.05)."""
        adf_stat, p_val, *_ = adfuller(serie.dropna())
        print(f"    ADF {nombre:<28} stat={adf_stat:.3f}  p={p_val:.4f}  "
              f"{'estacionaria ✓' if p_val < 0.05 else 'NO estacionaria ⚠'}")
        return p_val < 0.05

    print("\n  Test ADF de estacionariedad (requerido para Granger):")
    ipec_limpio   = df['ipec'].dropna()
    ratio_limpio  = df['ratio_crisis'].dropna()
    trends_limpio = df['narrativa_crisis_idx'].dropna()

    # Usar diferencias si no son estacionarias
    mask = df['ratio_crisis'].notna() & df['ipec'].notna() & df['narrativa_crisis_idx'].notna()
    df_clean = df[mask].copy()

    est_ipec   = test_estacionariedad(df_clean['ipec'],           'IPEC')
    est_ratio  = test_estacionariedad(df_clean['ratio_crisis'],   'ratio_crisis (titulares)')
    est_trends = test_estacionariedad(df_clean['narrativa_crisis_idx'], 'narrativa_crisis (Trends)')

    # Diferenciar si no estacionario
    if not est_ipec:
        df_clean['ipec_d']   = df_clean['ipec'].diff()
        target_col = 'ipec_d'
        print("    → Usando IPEC diferenciado")
    else:
        df_clean['ipec_d']   = df_clean['ipec']
        target_col = 'ipec_d'

    df_clean['ratio_d']  = df_clean['ratio_crisis'].diff()  if not est_ratio  else df_clean['ratio_crisis']
    df_clean['trends_d'] = df_clean['narrativa_crisis_idx'].diff() if not est_trends else df_clean['narrativa_crisis_idx']
    df_clean = df_clean.dropna()

    def run_granger(causa: str, efecto: str, max_lag: int = 6) -> dict:
        """Corre Granger y retorna el lag más significativo."""
        xy = df_clean[[efecto, causa]].dropna().values
        try:
            res = grangercausalitytests(xy, maxlag=max_lag, verbose=False)
        except Exception as e:
            return {"error": str(e)}
        summary = {}
        for lag in range(1, max_lag + 1):
            # Usar F-test (lrtest también disponible)
            f_stat = res[lag][0]['ssr_ftest'][0]
            p_val  = res[lag][0]['ssr_ftest'][1]
            summary[lag] = {'F': round(f_stat, 3), 'p': round(p_val, 4)}
        mejor = min(summary, key=lambda l: summary[l]['p'])
        return {
            'por_lag': summary,
            'mejor_lag': mejor,
            'F_mejor': summary[mejor]['F'],
            'p_mejor': summary[mejor]['p'],
            'significativo_p05': summary[mejor]['p'] < 0.05,
        }

    print(f"\n  Granger: ¿narrativa → IPEC?")
    print(f"  {'Test':<38} {'Mejor lag':>10} {'F':>8} {'p':>8} {'H₀ rechazada':>14}")
    print(f"  {'─'*38} {'─'*10} {'─'*8} {'─'*8} {'─'*14}")

    granger_tests = {
        'titulares → IPEC':       ('ratio_d',   target_col),
        'Google Trends → IPEC':   ('trends_d',  target_col),
        'IPEC → titulares (reverse)': (target_col, 'ratio_d'),
    }

    for nombre, (causa, efecto) in granger_tests.items():
        res = run_granger(causa, efecto)
        if 'error' in res:
            print(f"  {nombre:<38} ERROR: {res['error']}")
            continue
        sig = "✓ Sí (p<0.05)" if res['significativo_p05'] else "✗ No"
        print(f"  {nombre:<38} {res['mejor_lag']:>9} m  {res['F_mejor']:>7.3f}  "
              f"{res['p_mejor']:>7.4f}  {sig:>14}")
        resultados_granger[nombre] = res

    # Tabla detallada para el test principal
    if 'titulares → IPEC' in resultados_granger:
        res = resultados_granger['titulares → IPEC']
        print(f"\n  Detalle por lag — titulares ratio_crisis → IPEC:")
        print(f"  {'Lag':>5}   {'F':>8}   {'p':>8}   {'Sig':>6}")
        for lag, v in res['por_lag'].items():
            sig = "** p<0.01" if v['p'] < 0.01 else ("* p<0.05" if v['p'] < 0.05 else "")
            print(f"  {lag:>4}m   {v['F']:>7.3f}   {v['p']:>7.4f}   {sig}")


# ══════════════════════════════════════════════════════════════════
# RESUMEN FINAL Y COMPARACIÓN
# ══════════════════════════════════════════════════════════════════
print(f"\n{'='*65}")
print("RESUMEN COMPARATIVO")
print(f"{'='*65}")

# Extraer resultados clave
r_tit    = resultados_ccf['titulares_ratio_crisis']
r_trends = resultados_ccf['google_trends_narrativa']

print(f"\n  Proxy                     Mejor lag    r      p")
print(f"  ─────────────────────     ─────────  ──────  ──────")
print(f"  Titulares (medios reales) {r_tit['mejor_lag']:>7} meses  "
      f"{r_tit['r_mejor']:>+6.3f}  {r_tit['p_mejor']:.4f}")
print(f"  Google Trends (proxy)     {r_trends['mejor_lag']:>7} meses  "
      f"{r_trends['r_mejor']:>+6.3f}  {r_trends['p_mejor']:.4f}")

# Interpretación
mejor_proxy = "titulares" if abs(r_tit['r_mejor']) > abs(r_trends['r_mejor']) else "Google Trends"
print(f"\n  → Proxy con mayor correlación: {mejor_proxy}")
print(f"  → Lag de titulares: {r_tit['mejor_lag']} meses "
      f"({'≈ confirma' if abs(r_tit['mejor_lag'] - 6) <= 2 else 'difiere de'} "
      f"la hipótesis de lag=6)")

if STATSMODELS and 'titulares → IPEC' in resultados_granger:
    g = resultados_granger['titulares → IPEC']
    g_rev = resultados_granger.get('IPEC → titulares (reverse)', {})
    g_rev_sig = g_rev.get('significativo_p05', False)
    print(f"\n  Granger titulares → IPEC:  "
          f"{'✓ significativo' if g['significativo_p05'] else '✗ no significativo'} "
          f"(F={g.get('F_mejor','?'):.3f}, p={g.get('p_mejor','?'):.4f}, "
          f"lag={g['mejor_lag']}m)")
    print(f"  Granger IPEC → titulares:  "
          f"{'✓ significativo (causalidad inversa!)' if g_rev_sig else '✗ no significativo (direccionalidad correcta ✓)'}")

# Guardar JSON de resultados
output_json = {
    "ccf": resultados_ccf,
    "granger": resultados_granger,
    "n_meses": len(df),
    "periodo": f"{df['año_mes'].min()} – {df['año_mes'].max()}",
    "total_titulares": int(len(df_tit)),
    "ratio_crisis_promedio": float(mensual['ratio_crisis'].mean()),
}
def _json_serial(obj):
    if isinstance(obj, (np.integer,)):  return int(obj)
    if isinstance(obj, (np.floating,)): return float(obj)
    if isinstance(obj, (np.bool_,)):    return bool(obj)
    raise TypeError(f"No serializable: {type(obj)}")

OUT_GRANGER.write_text(json.dumps(output_json, ensure_ascii=False, indent=2, default=_json_serial))

# Guardar resumen en texto
resumen_lines = [
    "LA BRECHA NARRATIVA — Resultados Análisis Narrativa vs Percepción",
    "=" * 65,
    f"Período       : {df['año_mes'].min()} – {df['año_mes'].max()}",
    f"N meses       : {len(df)}",
    f"Total titulares: {len(df_tit)}",
    "",
    "CORRELACIÓN CRUZADA (proxy → IPEC, lag 0–12 meses):",
    f"  Titulares medios reales : lag={r_tit['mejor_lag']}m, r={r_tit['r_mejor']:+.4f}, p={r_tit['p_mejor']:.4f}",
    f"  Google Trends           : lag={r_trends['mejor_lag']}m, r={r_trends['r_mejor']:+.4f}, p={r_trends['p_mejor']:.4f}",
    "",
]
if STATSMODELS and 'titulares → IPEC' in resultados_granger:
    g = resultados_granger['titulares → IPEC']
    resumen_lines += [
        "TEST DE GRANGER:",
        f"  titulares → IPEC: F={g.get('F_mejor','?'):.3f}, p={g.get('p_mejor','?'):.4f}, lag={g['mejor_lag']}m",
    ]
resumen_lines += ["", f"Archivos: {OUT_SERIE.name}, {OUT_GRANGER.name}"]

OUT_RESUMEN.write_text("\n".join(resumen_lines), encoding='utf-8')
print(f"\n  Resultados guardados en:")
print(f"    {OUT_SERIE}")
print(f"    {OUT_GRANGER}")
print(f"    {OUT_RESUMEN}")
print()
