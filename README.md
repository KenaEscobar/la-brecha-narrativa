# La Brecha Narrativa 🇨🇱

**Análisis de la distancia entre la realidad económica medible y la percepción ciudadana en Chile (2014–2025)**

> *"El problema no es solo lo que pasa. Es lo que la gente cree que pasa — y quién construye esa creencia."*

---

## ¿Qué es esto?

Este proyecto investiga la brecha entre indicadores económicos objetivos (PIB, desempleo, salarios reales) y la percepción ciudadana sobre el estado del país, con foco en Chile entre 2014 y 2025.

La hipótesis central: **la narrativa mediática de crisis precede a la caída de la percepción ciudadana con un rezago de aproximadamente seis meses** — y esa narrativa puede amplificarse, acelerarse o fabricarse artificialmente, con consecuencias políticas reales para las personas más vulnerables.

---

## Conclusiones principales

La investigación combina encuestas CEP (2014–2025), el Índice de Percepción Económica IPEC del Banco Central, indicadores macroeconómicos reales, y un corpus de **5.010 titulares** de Emol y La Tercera recolectados desde Wayback Machine.

### La paradoja de 2015

En 2015, el PIB de Chile creció **+2,3%** y sin embargo el porcentaje de ciudadanos que decía que el país "estaba progresando" se desplomó de **43% a 16%** en menos de doce meses. La economía decía una cosa. La gente sentía otra.

### Los titulares predicen el IPEC con 6 meses de anticipación

El ratio de titulares de crisis en la prensa escrita correlaciona negativamente con el IPEC con un **lag de 6 meses** (r = −0,346, p = 0,0001). La correlación es significativa en todos los lags entre 0 y 12 meses.

| Proxy de narrativa | Mejor lag | r | p |
|---|---|---|---|
| **Titulares reales (Emol + La Tercera)** | **6 meses** | **−0,346** | **0,0001** |
| Google Trends "narrativa crisis" | 3 meses | −0,332 | 0,0002 |
| Google Trends "delincuencia" | 0 meses | −0,186 | 0,037 |

Los titulares reales superan a Google Trends como predictor: mayor correlación, señal persistente hasta 12 meses (vs. 6 de Trends).

### Causalidad estadística confirmada — con matiz

El test de Granger confirma que los titulares **Granger-causan** el IPEC (F = 4,95, p = 0,009, lag = 2m). Google Trends no pasa el mismo test (p = 0,095).

El matiz importante: la dirección inversa también es significativa (IPEC → titulares, p = 0,043, lag = 1m). La relación no es de una sola vía: los medios construyen narrativa que baja la percepción, y la percepción deteriorada retroalimenta más cobertura de crisis.

### El caso 2019

Los dos meses con mayor ratio de titulares de crisis en todo el corpus son **junio y agosto de 2019** — cuatro a seis meses antes del Estallido Social. Seis meses después de esos picos, el IPEC cayó −16,5 y −19,1 puntos respectivamente.

### La decadencia estructural post-2019

Desde 2022, el IPEC se recuperó lentamente (de 20,3 a ~40). Pero el CEP muestra que "Chile en decadencia" se mantiene en torno al **30%** — muy por encima de cualquier período anterior. Chile desarrolló una percepción estructural de declive que ya no responde mecánicamente a los indicadores económicos de corto plazo.

> Documento completo: [CONCLUSIONES.md](CONCLUSIONES.md)

---

## Estructura del repositorio

```
la-brecha-narrativa-chile/
│
├── 01_reconstruir_datasets.py      # Reconstruye todos los datasets desde fuentes públicas
├── 02_visualizacion_brecha.html    # Dashboard interactivo (standalone, sin servidor)
├── 03_scraping_titulares.py        # Recolecta titulares históricos desde Wayback Machine
├── 04_analisis_narrativa.py        # CCF + Granger: titulares vs. IPEC
│
├── brecha_data.json                # Dataset anual consolidado (para visualizaciones)
├── brecha_completo.json            # Dataset mensual completo (IPEC, CEP, Trends)
│
├── datos_procesados/
│   ├── pib_chile.csv               # PIB real anual, Banco Central
│   ├── gini_chile.csv              # Coeficiente GINI, World Bank
│   ├── pobreza_chile_13usd.csv     # Pobreza $6,85/día PPP, OWID/PIP
│   ├── cep_series_temporales.csv   # Encuestas CEP 71–95 (2014–2025)
│   ├── ipec_mensual.csv            # IPEC mensual 2014–2025
│   ├── macro_anual_chile.csv       # Dataset anual fusionado
│   ├── titulares_raw.csv           # 5.010 titulares Emol + La Tercera
│   ├── narrativa_vs_ipec.csv       # Serie mensual fusionada (titulares + IPEC + Trends)
│   └── resultados_granger.json     # Resultados estadísticos completos (CCF + Granger)
│
└── CONCLUSIONES.md                 # Documento de conclusiones completo
```

---

## Scripts — documentación

### `01_reconstruir_datasets.py`

Reconstruye todos los datasets del proyecto desde fuentes públicas o desde los valores documentados en el handoff.

**Fuentes:** World Bank (PIB, GINI), OWID/PIP (pobreza), Banco Central (IPEC), encuestas CEP, Google Trends (requiere descarga manual).  
**Output:** 7 archivos CSV/JSON en `datos_procesados/`.  
**Notas:** El IPEC y Google Trends son reconstrucciones interpoladas hasta disponer de los CSVs oficiales (BJ005.csv del Banco Central y descarga manual de Trends).

```bash
python3 01_reconstruir_datasets.py
```

---

### `02_visualizacion_brecha.html`

Dashboard interactivo standalone con tres pestañas:

- **La Brecha Central** — CEP "Chile Progresando" vs. IPEC anual vs. PIB real, con franjas por gobierno y líneas en eventos clave (2015, 2019, pandemia).
- **Narrativa vs Percepción** — IPEC mensual vs. índice de narrativa de crisis (Google Trends), serie de 143 puntos.
- **Delincuencia** — Búsquedas "delincuencia" en Chile 2014–2025 con región sombreada de crecimiento sostenido 2020–2024.

Los datos están embebidos directamente en el HTML. **Se abre con doble clic, sin servidor.**  
Requiere conexión a internet solo para cargar Chart.js desde cdnjs.

---

### `03_scraping_titulares.py`

Recolecta titulares históricos de Emol (portada y economía) y La Tercera (portada) desde **Wayback Machine** (archive.org), única fuente viable para datos históricos 2014–2025 (RSS directos bloqueados o eliminados).

**Estrategia:** CDX API para obtener 1 snapshot/mes por sección → descarga HTML → extrae h1/h2/h3 → clasifica tono por palabras clave.  
**Output:** `datos_procesados/titulares_raw.csv` (5.010 titulares).  
**Características:** reiniciable con checkpoint automático, retry con backoff exponencial, sleep entre requests para no sobrecargar Wayback.

```bash
python3 03_scraping_titulares.py            # correr completo (~40 min)
python3 03_scraping_titulares.py --dry-run  # simular sin requests
python3 03_scraping_titulares.py --reset    # borrar checkpoint y empezar de cero
python3 03_scraping_titulares.py --desde 2019-01  # reanudar desde fecha
```

**Limitación conocida:** La Tercera rediseñó su sitio en 2024, rompiendo el parser h2/h3 para el período 2024-07 a 2025-03.

---

### `04_analisis_narrativa.py`

Analiza la relación entre narrativa mediática (titulares reales) y percepción ciudadana (IPEC), comparando contra Google Trends como proxy.

**Análisis:**
1. Agrega titulares por mes → `ratio_crisis` (n_crisis / total)
2. Merge con IPEC mensual y Google Trends desde `brecha_completo.json`
3. Correlación cruzada (CCF) lag 0–12 para tres proxies
4. Test ADF de estacionariedad + test de Granger en ambas direcciones
5. Resumen comparativo y exportación de resultados

**Requiere:** `statsmodels` (`pip3 install statsmodels`)  
**Output:** `narrativa_vs_ipec.csv`, `resultados_granger.json`, `04_resultados.txt`

```bash
python3 04_analisis_narrativa.py
```

---

## Stack técnico y habilidades de ingeniería de datos

Este proyecto es también una demostración de un pipeline de datos completo, desde la recolección hasta el análisis estadístico, construido íntegramente con herramientas open source.

### Lenguaje y entorno

| Herramienta | Versión | Uso |
|---|---|---|
| Python | 3.13 | Pipeline completo |
| pandas | 2.2.3 | Manipulación, agregación y merge de datasets |
| numpy | 2.2.4 | Cálculos numéricos y normalización |
| scipy | — | Correlación de Pearson con p-values |
| statsmodels | 0.14.6 | Test ADF (estacionariedad) y causalidad de Granger |
| requests | 2.32.3 | HTTP client para scraping y APIs |
| BeautifulSoup4 | 4.15.0 | Parsing HTML de snapshots web |
| lxml | — | Parser HTML de alto rendimiento |
| Chart.js | 4.4.1 | Visualizaciones interactivas en el navegador |

### Recolección de datos — Web Scraping con resiliencia

El script `03_scraping_titulares.py` implementa un pipeline de scraping robusto sobre **Wayback Machine (archive.org)** — la única fuente viable para datos históricos 2014–2025, dado que los RSS directos de ambos medios están bloqueados o eliminados.

Técnicas implementadas:

- **CDX API de archive.org** — consulta programática del índice de Wayback para obtener timestamps de snapshots válidos por mes, URL y código de estado HTTP.
- **Retry con backoff exponencial** — cada request fallido reintenta con espera de 2ⁿ + jitter aleatorio, evitando thundering herd contra el servidor.
- **Rate limiting polite** — sleep configurable con variación aleatoria (±0,8s) entre requests para respetar los servidores y no ser bloqueada.
- **Checkpoint/resume pattern** — el estado de procesamiento se persiste en JSON después de cada N titulares. Si el script se interrumpe (timeout de red, corte de luz), se puede reanudar exactamente donde quedó sin repetir requests.
- **CLI con argparse** — interfaz de línea de comandos con flags `--dry-run`, `--reset` y `--desde YYYY-MM` para control granular de la ejecución.

```
432 snapshots × ~5s/request = ~36 min
3 secciones × 144 meses × retry logic + backoff
→ completado en ~45 min, 0 datos perdidos por interrupciones
```

### Arquitectura del pipeline

El proyecto sigue una arquitectura de pipeline de datos en etapas discretas y reproducibles:

```
Fuentes públicas
    │
    ▼
01_reconstruir_datasets.py     ← Ingesta y limpieza
    │  World Bank API · CEP handoff · Banco Central · Google Trends
    │
    ▼
brecha_completo.json           ← Datos maestros (IPEC, CEP, Trends, 143 meses)
brecha_data.json               ← Dataset agregado anual
    │
    ├──▶ 02_visualizacion_brecha.html   ← Capa de visualización
    │        Chart.js · plugins custom · datos embebidos (sin servidor)
    │
    ▼
03_scraping_titulares.py       ← Recolección de datos primarios
    │  Wayback CDX API · BeautifulSoup4 · checkpoint/resume
    │
    ▼
titulares_raw.csv              ← 5.010 titulares clasificados
    │
    ▼
04_analisis_narrativa.py       ← Análisis estadístico
    │  CCF · ADF · Granger · merge con IPEC
    │
    ▼
narrativa_vs_ipec.csv          ← Serie fusionada lista para modelado
resultados_granger.json        ← Output estadístico reproducible
```

Cada etapa es **idempotente**: puede correrse de nuevo sin efectos secundarios. Los outputs intermedios son archivos planos (CSV/JSON) — no hay dependencias de bases de datos ni servicios externos en tiempo de análisis.

### Análisis estadístico

**Correlación cruzada (CCF)**  
Implementación manual sobre series normalizadas (z-score), sin depender de la CCF de statsmodels, para tener control explícito sobre los lags y los p-values por Pearson. Se calcularon lags 0–12 para tres proxies en paralelo.

**Test de Dickey-Fuller aumentado (ADF)**  
Aplicado antes del test de Granger para verificar estacionariedad, con diferenciación automática de las series que no la cumplen. Esto evita regresiones espurias entre series integradas.

**Test de causalidad de Granger**  
Aplicado en ambas direcciones (narrativa→IPEC e IPEC→narrativa) con lags 1–6. Usar ambas direcciones es la práctica estándar para distinguir precedencia estadística de correlación bidireccional — el hallazgo de retroalimentación surgió precisamente de esta doble verificación.

### Visualización — Dashboard standalone

`02_visualizacion_brecha.html` es un dashboard de producción construido sin frameworks:

- **Chart.js 4.4.1** con plugins custom escritos en JS vanilla para líneas verticales con etiquetas rotadas y regiones sombreadas por período de gobierno.
- **Datos embebidos directamente en el HTML** (46 KB de JSON minificado) para que funcione abriendo el archivo con doble clic, sin necesidad de servidor local ni conexión de red.
- **SRI hash verificado** (`sha512`) sobre el único CDN externo (Chart.js) para garantizar integridad del script.
- **Doble eje Y**, tooltips con mes/año exacto, franjas por gobierno calculadas dinámicamente con `findIndex` sobre los datos reales.

### Reproducibilidad

Todos los análisis son reproducibles desde cero con:

```bash
python3 01_reconstruir_datasets.py   # reconstruir datos base
python3 03_scraping_titulares.py     # recolectar titulares (~45 min)
python3 04_analisis_narrativa.py     # correr análisis estadístico
```

Las únicas dependencias externas son `pip3 install requests beautifulsoup4 lxml statsmodels` y una conexión a internet para el scraping.

---

## Estado actual

- [x] Reconstrucción de datasets (PIB, GINI, pobreza, CEP, IPEC)
- [x] Dashboard interactivo con tres pestañas y franjas por gobierno
- [x] Scraping de 5.010 titulares históricos (Emol + La Tercera, 2014–2025)
- [x] Análisis CCF y Granger: titulares vs. IPEC
- [x] Documento de conclusiones
- [ ] Clasificador NLP (reemplazar palabras clave por modelo de lenguaje)
- [ ] Expansión del corpus: televisión, redes sociales
- [ ] Análisis por nivel socioeconómico / región
- [ ] Informe público Fase 1

---

## Fuentes de datos

Todos los datos utilizados son de **fuentes públicas y abiertas**:

| Dataset | Fuente | Acceso |
|---|---|---|
| Encuestas CEP 71–95 | Centro de Estudios Públicos | cepchile.cl |
| IPEC mensual | Banco Central de Chile (BJ005) | si3.bcentral.cl |
| PIB real anual | Banco Central de Chile | si3.bcentral.cl |
| GINI | World Bank | data.worldbank.org |
| Pobreza ($6,85/día) | Our World in Data / PIP | ourworldindata.org |
| Titulares históricos | Wayback Machine (archive.org) | web.archive.org |
| Google Trends | Google Trends | trends.google.com |

---

## Por qué esto importa

Chile tiene una conversación pública profundamente distorsionada. Las personas que más dependen del Estado — servicios de salud, educación pública, transporte — son las más afectadas cuando la narrativa de crisis se instala artificialmente y desplaza otras prioridades del debate.

Este proyecto no tiene financiamiento institucional ni agenda política partidaria. Es investigación ciudadana con datos abiertos.

---

## Contacto y colaboración

¿Eres periodista, investigador/a, o simplemente te interesa el tema? Abre un Issue o escríbeme.

---

# The Narrative Gap 🇨🇱

**Analyzing the distance between measurable economic reality and citizen perception in Chile (2014–2025)**

> *"The problem isn't just what happens. It's what people believe is happening — and who builds that belief."*

---

## What is this?

This project investigates the gap between objective economic indicators (GDP, unemployment, real wages) and citizen perception of the country's situation, focusing on Chile from 2014 to 2025.

The central hypothesis: **media crisis narratives statistically precede falls in citizen economic perception by approximately six months** — and those narratives can be amplified, accelerated, or manufactured, with real political consequences for the most vulnerable.

---

## Key findings

Based on 5,010 headlines from Emol and La Tercera (scraped from Wayback Machine), IPEC monthly data, CEP surveys (2014–2025), and macroeconomic indicators:

- Real newspaper headlines predict the IPEC **6 months in advance** (r = −0.346, p = 0.0001), outperforming Google Trends as a proxy.
- Granger causality test confirms headlines → IPEC (F = 4.95, p = 0.009). Google Trends does not pass the same test (p = 0.095).
- The relationship is **bidirectional**: deteriorated perception also feeds more crisis coverage (IPEC → headlines, lag = 1m). Not a one-way street — a feedback loop.
- The two months with the highest crisis headline ratios in the entire corpus are **June and August 2019** — four to six months before the Social Uprising (Estallido Social).
- Since 2022, the IPEC has slowly recovered but CEP "Chile in decline" sentiment remains at ~30%, far above any prior period — suggesting a structural perception of decline that no longer responds mechanically to short-term economic indicators.

Full conclusions document (in Spanish): [CONCLUSIONES.md](CONCLUSIONES.md)

---

## Current status

- [x] Dataset reconstruction (GDP, GINI, poverty, CEP surveys, IPEC)
- [x] Interactive dashboard (3-tab standalone HTML)
- [x] Historical headline scraping — 5,010 headlines (Emol + La Tercera, 2014–2025)
- [x] CCF and Granger analysis: headlines vs. IPEC
- [x] Conclusions document
- [ ] NLP classifier (replace keyword matching with language model)
- [ ] Corpus expansion: TV news transcripts, social media
- [ ] Phase 1 public report

---

## Why this matters

Chile's public conversation is deeply distorted. People who depend most on the State — public health, education, transportation — are most affected when crisis narratives artificially crowd out other priorities from public debate.

This project has no institutional funding and no partisan political agenda. It is citizen research with open data.

---

## Contact & collaboration

Are you a journalist, researcher, or just interested in the topic? Open an Issue or reach out.
