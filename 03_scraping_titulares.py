"""
La Brecha Narrativa — Script 03: Scraping de Titulares
=======================================================
Recolecta titulares históricos de Emol y La Tercera desde Wayback Machine.

FUENTE: archive.org CDX API + snapshots HTML
  Estrategia: 1 snapshot/mes por sección → extraer h1/h2/h3 → clasificar tono
  Alternativa directa descartada: Emol bloquea bots, La Tercera RSS da 404.

PERÍODO: 2014–2025 (144 meses × 3 secciones = ~432 snapshots)
  Tiempo estimado: ~35–50 min a 2.5s/request (depende de latencia de Wayback)

OUTPUT:
  datos_procesados/titulares_raw.csv
  datos_procesados/titulares_checkpoint.json  ← permite reanudar si se interrumpe

USO:
  python3 03_scraping_titulares.py           # correr normal
  python3 03_scraping_titulares.py --dry-run # simular sin requests
  python3 03_scraping_titulares.py --reset   # borrar checkpoint y empezar de cero
  python3 03_scraping_titulares.py --desde 2019-01  # reanudar desde fecha específica
"""

import json
import time
import random
import argparse
import warnings
import requests
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# ─── Rutas ────────────────────────────────────────────────────────────────────
BASE       = Path(__file__).parent
PROC       = BASE / "datos_procesados"
PROC.mkdir(exist_ok=True)
OUT_CSV    = PROC / "titulares_raw.csv"
CHECKPOINT = PROC / "titulares_checkpoint.json"

# ─── Red ──────────────────────────────────────────────────────────────────────
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (compatible; research-bot/1.0; '
        'proyecto-academico la-brecha-narrativa-chile; '
        'contacto: github.com/KenaEscobar/la-brecha-narrativa)'
    )
}
SLEEP_BASE   = 2.5   # segundos entre requests
SLEEP_JITTER = 0.8   # variación aleatoria ±
TIMEOUT      = 35
MAX_RETRIES  = 3
SAVE_EVERY   = 15    # guardar CSV + checkpoint cada N titulares nuevos

# ─── Secciones a scrapear ─────────────────────────────────────────────────────
# Verificadas manualmente: cobertura confirmada desde 2014 en Wayback Machine
TARGETS = [
    {"medio": "emol",       "seccion": "portada",  "url": "http://www.emol.com/"},
    {"medio": "emol",       "seccion": "economia", "url": "http://www.emol.com/economia/"},
    {"medio": "la_tercera", "seccion": "portada",  "url": "http://www.latercera.com/"},
]

# ─── Clasificación de tono ────────────────────────────────────────────────────
PALABRAS_CRISIS = [
    "crisis", "caos", "colapso", "derrumbe", "estallido", "pánico", "panico",
    "desplome", "catástrofe", "catastrofe", "alarma", "emergencia", "quiebra",
    "recesión", "recesion", "default", "impago", "paralización", "paralizacion",
]
PALABRAS_POSITIVO = [
    "crecimiento", "récord", "record", "mejora", "avance", "recuperación",
    "recuperacion", "auge", "alza", "logro", "éxito", "exito", "expansión",
    "expansion", "acuerdo", "inversión", "inversion", "empleo", "superávit", "superavit",
]

def clasificar_tono(titular: str) -> str:
    t = titular.lower()
    if any(k in t for k in PALABRAS_CRISIS):
        return "crisis"
    if any(k in t for k in PALABRAS_POSITIVO):
        return "positivo"
    return "neutro"

# ─── Navegación ruidosa que no es un titular ──────────────────────────────────
NAV_NOISE = {
    "inicio", "home", "política", "politica", "economía", "economia",
    "deportes", "internacional", "tecnología", "tecnologia", "tendencias",
    "especiales", "edición impresa", "edicion impresa", "opinión", "opinion",
    "cultura", "mundo", "chile", "sociedad", "bienvenido",
}

# ─── Utilidades de red ────────────────────────────────────────────────────────
def get_with_retry(url: str) -> requests.Response | None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False)
            return r
        except requests.exceptions.RequestException as e:
            espera = (2 ** attempt) + random.uniform(0, 2)
            print(f"    ↻ Intento {attempt}/{MAX_RETRIES} falló ({type(e).__name__}). "
                  f"Reintentando en {espera:.1f}s...")
            if attempt < MAX_RETRIES:
                time.sleep(espera)
    return None

def dormir():
    t = SLEEP_BASE + random.uniform(-SLEEP_JITTER, SLEEP_JITTER)
    time.sleep(max(1.0, t))

# ─── Wayback CDX API ──────────────────────────────────────────────────────────
def get_snapshot_timestamp(url: str, año: int, mes: int) -> str | None:
    """
    Busca el timestamp del snapshot más cercano al día 15 del mes.
    Usa la CDX API de archive.org (pública, sin autenticación).
    """
    # Buscar entre días 10-25 del mes para evitar snapshots de principio/fin
    from_ts = f"{año}{mes:02d}10000000"
    to_ts   = f"{año}{mes:02d}25235959"
    cdx_url = (
        f"http://web.archive.org/cdx/search/cdx"
        f"?url={url}"
        f"&output=json"
        f"&from={from_ts}&to={to_ts}"
        f"&fl=timestamp"
        f"&filter=statuscode:200"
        f"&limit=1"
    )
    r = get_with_retry(cdx_url)
    if r is None or r.status_code != 200:
        return None
    try:
        data = json.loads(r.text)
        # data[0] es el header ["timestamp"], data[1] es el primer resultado
        if len(data) < 2:
            return None
        return data[1][0]
    except (json.JSONDecodeError, IndexError):
        return None

def fetch_snapshot_html(original_url: str, timestamp: str) -> str | None:
    """Descarga el HTML de un snapshot de Wayback."""
    wayback_url = f"https://web.archive.org/web/{timestamp}/{original_url}"
    r = get_with_retry(wayback_url)
    if r is None or r.status_code != 200:
        return None
    # Wayback puede devolver redirect con 200 pero cuerpo vacío
    if len(r.content) < 5000:
        return None
    return r.text

# ─── Extracción de titulares ──────────────────────────────────────────────────
def extraer_titulares(html: str) -> list[str]:
    """
    Extrae titulares de un snapshot HTML.
    Elimina nav/footer/script antes de parsear para reducir ruido.
    Devuelve máximo 40 titulares únicos, filtrados por calidad.
    """
    soup = BeautifulSoup(html, 'lxml')

    # Limpiar elementos que no son contenido editorial
    for tag in soup.find_all(['nav', 'footer', 'script', 'style', 'aside',
                               'header', 'form', 'button']):
        tag.decompose()

    vistos  = set()
    titulares = []

    for tag in soup.find_all(['h1', 'h2', 'h3']):
        t = tag.get_text(separator=' ', strip=True)

        # Filtros de calidad
        if len(t) < 25 or len(t) > 280:
            continue
        if t.lower() in NAV_NOISE:
            continue
        # Descartar si es todo mayúsculas (suele ser sección/menú)
        if t.isupper():
            continue
        # Descartar si no tiene al menos una letra minúscula (camelCase o normal)
        if not any(c.islower() for c in t):
            continue
        if t in vistos:
            continue

        vistos.add(t)
        titulares.append(t)

        if len(titulares) >= 40:
            break

    return titulares

# ─── Checkpoint ───────────────────────────────────────────────────────────────
def load_checkpoint() -> dict:
    if CHECKPOINT.exists():
        return json.loads(CHECKPOINT.read_text(encoding='utf-8'))
    return {"procesados": [], "total_titulares": 0, "errores": []}

def save_checkpoint(ckpt: dict):
    CHECKPOINT.write_text(
        json.dumps(ckpt, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )

def ckpt_key(medio: str, seccion: str, año: int, mes: int) -> str:
    return f"{medio}:{seccion}:{año}:{mes:02d}"

# ─── Pipeline principal ───────────────────────────────────────────────────────
def run(dry_run: bool = False, reset: bool = False, desde: str | None = None):
    if reset:
        for f in [CHECKPOINT, OUT_CSV]:
            if f.exists():
                f.unlink()
        print("Checkpoint y CSV eliminados — comenzando desde cero.")

    ckpt      = load_checkpoint()
    procesados = set(ckpt["procesados"])

    # Cargar CSV existente para no perder datos previos
    rows: list[dict] = []
    if OUT_CSV.exists():
        df_prev = pd.read_csv(OUT_CSV, encoding='utf-8')
        rows = df_prev.to_dict('records')
        print(f"Continuando — {len(rows)} titulares ya recolectados.")

    # Filtro de fecha de inicio (--desde YYYY-MM)
    desde_año, desde_mes = 2014, 1
    if desde:
        try:
            desde_año, desde_mes = int(desde[:4]), int(desde[5:7])
        except (ValueError, IndexError):
            print(f"⚠ Formato --desde inválido (usar YYYY-MM). Ignorando.")

    nuevos_desde_checkpoint = 0

    print("=" * 65)
    print("LA BRECHA NARRATIVA — Scraping de titulares (Wayback Machine)")
    print("=" * 65)

    total_snapshots = len(TARGETS) * 144
    ya_hechos       = len(procesados)
    pendientes      = total_snapshots - ya_hechos
    est_min         = pendientes * (SLEEP_BASE * 2) / 60

    print(f"Secciones     : {len(TARGETS)} ({', '.join(t['medio']+'/'+t['seccion'] for t in TARGETS)})")
    print(f"Período       : 2014–2025 ({total_snapshots} snapshots totales)")
    print(f"Ya procesados : {ya_hechos}  |  Pendientes: {pendientes}")
    print(f"Tiempo estimado: ~{est_min:.0f}–{est_min*1.5:.0f} min")
    if dry_run:
        print("⚠  DRY RUN — no se hacen requests ni se guardan datos")
    print()

    for target in TARGETS:
        medio   = target["medio"]
        seccion = target["seccion"]
        url     = target["url"]

        print(f"\n{'─'*65}")
        print(f"  {medio.upper()} / {seccion}")
        print(f"{'─'*65}")

        for año in range(2014, 2026):
            for mes in range(1, 13):
                # Respetar filtro --desde
                if (año, mes) < (desde_año, desde_mes):
                    continue

                key   = ckpt_key(medio, seccion, año, mes)
                label = f"{año}-{mes:02d}"

                if key in procesados:
                    continue

                if dry_run:
                    print(f"  [{label}] DRY RUN — saltando")
                    continue

                # ── Paso 1: obtener timestamp del snapshot ──────────────────
                print(f"  [{label}] CDX...", end='', flush=True)
                dormir()
                timestamp = get_snapshot_timestamp(url, año, mes)

                if not timestamp:
                    print(f" sin snapshot")
                    procesados.add(key)
                    ckpt["procesados"].append(key)
                    continue

                # ── Paso 2: descargar HTML ──────────────────────────────────
                print(f" ts={timestamp[:10]}...", end='', flush=True)
                dormir()
                html = fetch_snapshot_html(url, timestamp)

                if not html:
                    print(f" error al descargar")
                    ckpt["errores"].append(f"{key}:{timestamp}")
                    continue

                # ── Paso 3: extraer y clasificar ────────────────────────────
                titulares = extraer_titulares(html)
                print(f" {len(titulares)} titulares", end='')

                url_snapshot = f"https://web.archive.org/web/{timestamp}/{url}"
                fecha_str    = f"{año}-{mes:02d}-15"

                for titular in titulares:
                    rows.append({
                        "fecha":         fecha_str,
                        "año":           año,
                        "mes":           mes,
                        "medio":         medio,
                        "seccion":       seccion,
                        "titular":       titular,
                        "url_snapshot":  url_snapshot,
                        "tono_estimado": clasificar_tono(titular),
                    })

                nuevos_desde_checkpoint += len(titulares)
                procesados.add(key)
                ckpt["procesados"].append(key)
                ckpt["total_titulares"] = len(rows)

                # ── Checkpoint periódico ────────────────────────────────────
                if nuevos_desde_checkpoint >= SAVE_EVERY:
                    pd.DataFrame(rows).to_csv(OUT_CSV, index=False, encoding='utf-8')
                    save_checkpoint(ckpt)
                    print(f"  ← checkpoint ({len(rows)} total)", end='')
                    nuevos_desde_checkpoint = 0

                print()  # newline tras la línea de progreso

    # ── Guardar resultado final ───────────────────────────────────────────────
    if not dry_run:
        df = pd.DataFrame(rows)
        df.to_csv(OUT_CSV, index=False, encoding='utf-8')
        save_checkpoint(ckpt)

        print(f"\n{'='*65}")
        print(f"COMPLETADO")
        print(f"{'='*65}")
        print(f"Total titulares : {len(df)}")
        print(f"Output          : {OUT_CSV}")
        print()

        if len(df) > 0:
            print("Distribución de tono:")
            for tono, n in df['tono_estimado'].value_counts().items():
                pct = n / len(df) * 100
                print(f"  {tono:<10} {n:5d}  ({pct:.1f}%)")

            print("\nTitulares por medio/sección:")
            for (medio, sec), n in df.groupby(['medio','seccion']).size().items():
                print(f"  {medio}/{sec:<12} {n:5d}")

            print("\nAños con menos de 5 titulares (posibles gaps de cobertura):")
            por_año = df.groupby('año').size()
            gaps    = por_año[por_año < 5]
            if len(gaps):
                print(f"  {gaps.to_dict()}")
            else:
                print("  Ninguno ✓")

            print(f"\nPróximo paso:")
            print(f"  Ejecutar 04_analisis_narrativa.py para correlación titulares vs IPEC")
    else:
        print(f"\nDRY RUN completado.")
        print(f"Se procesarían {len(TARGETS) * 144} snapshots.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='La Brecha Narrativa — Scraping de titulares desde Wayback Machine'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Simular sin hacer requests ni guardar datos'
    )
    parser.add_argument(
        '--reset', action='store_true',
        help='Eliminar checkpoint y CSV existente, comenzar desde cero'
    )
    parser.add_argument(
        '--desde', metavar='YYYY-MM', default=None,
        help='Procesar solo desde esta fecha (ej: 2019-01)'
    )
    args = parser.parse_args()
    run(dry_run=args.dry_run, reset=args.reset, desde=args.desde)
