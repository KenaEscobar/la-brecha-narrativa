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
