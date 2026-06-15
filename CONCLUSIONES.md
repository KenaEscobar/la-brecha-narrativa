# La Brecha Narrativa — Chile 2014–2025
## Documento de Conclusiones

**Autora:** Kena Escobar  
**Fecha:** junio 2026  
**Fuentes:** CEP Chile (encuestas 71–95) · Banco Central IPEC BJ005 · PIB real · Emol · La Tercera · Google Trends CL · World Bank

---

## 1. Planteamiento

Este proyecto nació de una observación incómoda: en 2015, el PIB de Chile creció un 2,3% y sin embargo la proporción de ciudadanos que decía que el país "estaba progresando" se desplomó de 43,3% a 16,6% en menos de doce meses. La economía decía una cosa. La gente sentía otra.

La hipótesis central que guió la investigación fue la siguiente:

> **La narrativa mediática de crisis precede a la caída de la percepción ciudadana sobre la economía, con un rezago aproximado de seis meses. Esa narrativa puede amplificarse, acelerarse o fabricarse artificialmente — y tiene consecuencias políticas reales para las personas más vulnerables.**

Para contrastar esta hipótesis se construyeron tres fuentes de evidencia independientes: el Índice de Percepción Económica (IPEC) del Banco Central como medida de percepción ciudadana, búsquedas de Google Trends como proxy inicial de narrativa, y un corpus de 5.010 titulares reales de Emol y La Tercera recolectados desde Wayback Machine como validación con datos primarios.

---

## 2. Metodología en síntesis

| Componente | Fuente | Período | N |
|---|---|---|---|
| Percepción ciudadana | IPEC BJ005 (Banco Central) | 2014–2025 | 143 meses |
| Encuestas de opinión | CEP encuestas 71–95 | 2014–2025 | 23 encuestas |
| Proxy de narrativa (fase 1) | Google Trends CL | 2014–2025 | 143 meses |
| Narrativa mediática real (fase 2) | Emol portada, Emol economía, La Tercera portada | 2014–2025 | 5.010 titulares |
| Indicadores económicos | PIB real, GINI, Pobreza (World Bank / Banco Central) | 2010–2024 | — |

El análisis estadístico incluyó:
- **Correlación cruzada (CCF)** con lags 0–12 meses entre cada proxy de narrativa y el IPEC.
- **Test de Dickey-Fuller aumentado (ADF)** para verificar estacionariedad antes del test de Granger.
- **Test de causalidad de Granger** en ambas direcciones (narrativa → IPEC e IPEC → narrativa) para distinguir precedencia estadística de correlación espuria.

---

## 3. Hallazgo 1 — La brecha de 2015 no fue una anomalía

El colapso de la percepción ciudadana en 2015 fue el punto de partida empírico de la investigación. Los datos confirman su magnitud y su carácter paradójico:

- Chile Progresando (CEP): **43,3% → 16,6%** entre julio de 2014 y abril de 2015 (caída de 26,7 puntos).
- PIB real en 2015: **+2,3%** (crecimiento positivo y sostenido).
- IPEC promedio 2014: **48,1** → IPEC promedio 2015: **37,6** (caída de 10,5 puntos).

La economía creció. La percepción colapsó. Esa brecha necesita una explicación que los modelos económicos convencionales no proveen — y la narrativa mediática es la candidata más parsimoniosa.

Lo que hace especialmente significativa esta brecha es su *velocidad*: el desplome ocurrió en menos de un año, mucho más rápido que cualquier deterioro real de los indicadores objetivos. La velocidad de la caída es una firma característica de la influencia narrativa.

---

## 4. Hallazgo 2 — Los titulares predicen el IPEC con un rezago de 6 meses

El resultado estadístico central de la investigación es el siguiente:

**Correlación cruzada: ratio de titulares de crisis → IPEC**

| Lag (meses) | r | p |
|---|---|---|
| 0 | −0,255 | 0,004 |
| 1 | −0,221 | 0,013 |
| 2 | −0,292 | 0,001 |
| 3 | −0,299 | 0,001 |
| 4 | −0,327 | 0,0002 |
| 5 | −0,327 | 0,0002 |
| **6** | **−0,346** | **0,0001** |
| 7 | −0,327 | 0,0003 |
| 8 | −0,334 | 0,0002 |
| 9 | −0,302 | 0,001 |
| 10 | −0,294 | 0,001 |
| 11 | −0,246 | 0,008 |
| 12 | −0,207 | 0,027 |

Tres observaciones son relevantes:

**Primera:** La correlación es negativa en todos los lags y significativa (p < 0,05) en todos ellos — incluyendo el contemporáneo (lag=0). Esto significa que los titulares de crisis coexisten con un IPEC bajo, los preceden, y los siguen acompañando. No hay un momento en que la narrativa y la percepción estén desconectadas.

**Segunda:** El pico de correlación se ubica exactamente en **lag = 6 meses** (r = −0,346, p = 0,0001), confirmando la hipótesis de trabajo. Un aumento en el ratio de titulares de crisis en el mes T se asocia con una caída del IPEC en T+6.

**Tercera:** La correlación se mantiene significativa hasta el lag 12 (r = −0,207, p = 0,027). El efecto de la narrativa sobre la percepción no es puntual: es persistente durante al menos un año.

---

## 5. Hallazgo 3 — Los titulares reales son mejor predictor que Google Trends

La comparación entre los tres proxies de narrativa arroja un resultado relevante para la metodología:

| Proxy | Mejor lag | r máximo | p | Persistencia |
|---|---|---|---|---|
| **Titulares (Emol + La Tercera)** | **6 meses** | **−0,346** | **0,0001** | Significativo hasta lag 12 |
| Google Trends "narrativa crisis" | 3 meses | −0,332 | 0,0002 | Significativo hasta lag 6 |
| Google Trends "delincuencia" | 0 meses | −0,186 | 0,037 | Solo lag 0 |

Los titulares reales tienen una correlación más alta que Google Trends y, crucialmente, su señal persiste el doble de tiempo (12 meses vs. 6 meses). Google Trends captura lo que la gente *busca* después de haber sido expuesta a la narrativa; los titulares capturan la narrativa en su punto de origen.

La "delincuencia" como proxy resulta ser el más débil de los tres: su correlación no persiste más allá del momento contemporáneo, lo que sugiere que es más un síntoma reactivo que un precursor de la percepción económica general.

---

## 6. Hallazgo 4 — Test de Granger: los titulares causan (estadísticamente) el IPEC, pero hay retroalimentación

El test de causalidad de Granger permite ir más allá de la correlación y preguntar: ¿los titulares tienen poder predictivo *adicional* sobre el IPEC, más allá de la inercia del propio IPEC?

| Dirección | F (mejor lag) | p | Lag | Conclusión |
|---|---|---|---|---|
| Titulares → IPEC | 4,951 | **0,0086** | 2 meses | ✓ Significativo (p < 0,01) |
| Google Trends → IPEC | 1,855 | 0,095 | 6 meses | ✗ No significativo |
| IPEC → Titulares | 4,195 | **0,043** | 1 mes | ✓ Significativo (p < 0,05) |

Los titulares Granger-causan el IPEC con p = 0,0086 — resultado sólido. Google Trends, en cambio, no pasa el test formal de Granger (p = 0,095), lo que refuerza que es un proxy más ruidoso de la narrativa real.

**El hallazgo más matizado es el de la dirección inversa:** el IPEC también Granger-causa los titulares (p = 0,043, lag = 1 mes). Esto no invalida la hipótesis principal — las dos cosas pueden ser ciertas a la vez — sino que revela la dinámica real del sistema:

> Los medios construyen narrativa que baja la percepción ciudadana (lag 6m). Y cuando la percepción ya cayó, los medios la amplifican (lag 1m). **No es solo un efecto unidireccional: es un ciclo de retroalimentación.**

La causalidad no va solo de los medios al ciudadano. Va también del estado emocional colectivo de vuelta a la agenda mediática. Los medios amplifican lo que la gente ya siente, y esa amplificación profundiza el sentimiento.

---

## 7. Hallazgo 5 — El caso más claro: 2019

El año 2019 ofrece el caso más limpio de la hipótesis en acción. Los dos meses con mayor ratio de titulares de crisis en todo el corpus son junio y agosto de 2019 — cuatro a seis meses *antes* del Estallido Social de octubre.

| Mes | Ratio crisis | IPEC (mes) | IPEC (6m después) | Δ IPEC |
|---|---|---|---|---|
| Jun 2019 | 20,0% | 37,8 | 21,2 | **−16,5** |
| Ago 2019 | 14,3% | 39,4 | 20,3 | **−19,1** |
| Nov 2019 | 11,1% | 28,3 | 25,5 | −2,8 |

La narrativa de crisis en los medios precedió al Estallido Social en el tiempo. No es posible establecer causalidad definitiva desde este análisis — el deterioro social que derivó en el estallido fue real y multifactorial. Pero la construcción narrativa previa también fue real, y los datos muestran que esa narrativa antecedió estadísticamente al colapso de la percepción ciudadana.

Una lectura más incómoda: parte de los titulares de junio–agosto 2019 amplificaban tensiones sociales genuinas; otra parte anticipaba una narrativa de crisis que luego se autocumplió. La distinción entre ambas es imposible de hacer solo con datos cuantitativos — y esa limitación es honesta.

---

## 8. Hallazgo 6 — La excepción de 2023–2024

El corpus también revela un contraejemplo que merece atención: el período 2023–2024 tiene tasas de crisis en titulares comparativamente altas (6,4% en 2023, 5,7% en 2024), pero el IPEC no cae con la misma magnitud que en 2019–2020.

| Período | Ratio crisis | IPEC promedio |
|---|---|---|
| 2019 | 4,9% | 39,2 |
| 2020 | 3,1% | 26,4 |
| 2023 | 6,4% | 28,4 |
| 2024 | 5,7% | 31,3 |

Una interpretación posible: el IPEC ya estaba en niveles históricamente bajos desde el Estallido y la pandemia. La percepción ciudadana puede haber alcanzado un *piso estructural* del que es difícil caer más, independientemente de la narrativa mediática. Cuando la percepción ya está deteriorada, la narrativa de crisis pierde capacidad marginal de empeorarla.

Esto sugiere que la relación entre narrativa y percepción no es lineal: su efecto es mayor cuando parte de una percepción relativamente alta. Dicho de otro modo, **la narrativa de crisis es más poderosa cuando tiene más que destruir**.

---

## 9. El patrón estructural: lo que el IPEC y el CEP dicen juntos

Leyendo IPEC y CEP en conjunto, emerge un patrón que trasciende cualquier gobierno particular:

- **Bajo Bachelet II (2014–2018):** El desplome fue el más dramático y más rápido. Chile Progresando cayó 26 puntos en un año con economía creciente. El IPEC cayó de 54,6 a 37,0 entre enero 2014 y diciembre 2015.

- **Bajo Piñera II (2018–2022):** Recuperación inicial fuerte (IPEC volvió a ~52 en 2018), seguida de caída gradual pre-Estallido y colapso total durante pandemia (mínimo histórico 20,3 en junio 2020).

- **Bajo Boric (2022–2025):** El IPEC muestra recuperación lenta pero sostenida desde el mínimo (20,3 → 40,6 en noviembre 2025). Sin embargo, el CEP muestra que "Chile en Decadencia" se mantiene en torno al 30% — significativamente más alto que cualquier período anterior. La percepción de avance nunca se recuperó.

Lo más llamativo es que **bajo Boric el IPEC sube pero el sentimiento de decadencia en el CEP se mantiene alto**. IPEC e CEP miden cosas distintas: el IPEC mide expectativas económicas coyunturales; el CEP captura una sensación más profunda sobre el rumbo del país. La disociación entre ambos sugiere que Chile desarrolló, especialmente desde 2019, una **percepción estructural de declive** que ya no responde mecánicamente a los indicadores económicos de corto plazo.

---

## 10. Limitaciones

Esta investigación tiene límites claros que deben declararse antes de cualquier uso de sus conclusiones.

**Del corpus de titulares:** Los 5.010 titulares cubren solo Emol portada, Emol economía y La Tercera portada. Quedan fuera: televisión (principal medio de consumo informativo), radio, redes sociales, medios regionales, y medios de nicho político. La muestra es representativa de la prensa escrita histórica de referencia, no del ecosistema mediático completo.

**De la clasificación de tono:** El método de palabras clave es una aproximación de primer orden. El 92,5% de los titulares quedó clasificado como "neutro" — lo que indica que el clasificador es conservador y probablemente subestima los titulares de crisis que usan vocabulario elusivo ("complejidad", "incertidumbre", "tensión"). Un clasificador de lenguaje natural (NLP) daría resultados más sensibles.

**Del gap de cobertura:** La Tercera rediseñó su sitio web en 2024, lo que impidió extraer titulares entre julio 2024 y marzo 2025 con el parser de h2/h3. Los resultados de ese período subestiman la cobertura real.

**De la causalidad:** El test de Granger establece precedencia estadística en un modelo bivariado, no causalidad en el sentido filosófico. No se puede descartar que una tercera variable (deterioro económico real anticipado, tensiones sociales previas al estallido, etc.) explique tanto el aumento de titulares de crisis como la caída posterior del IPEC. La hipótesis es consistente con los datos, pero no es la única explicación posible.

**Del período de análisis:** 126 meses es una serie suficiente para análisis de correlación, pero relativamente corta para análisis de series de tiempo con múltiples quiebres estructurales (2015, 2019, 2020, 2022). Los resultados deben interpretarse con cautela ante esos quiebres.

---

## 11. Conclusión central

Los datos de esta investigación son consistentes con la siguiente afirmación:

> **En Chile entre 2014 y 2025, la narrativa mediática de crisis en la prensa escrita precede estadísticamente a la caída de la percepción económica ciudadana con un rezago de seis meses. Los titulares de Emol y La Tercera son mejor predictor del IPEC futuro que las búsquedas en Google Trends, y su poder predictivo persiste durante doce meses. La relación no es unidireccional: existe retroalimentación en la que la percepción deteriorada también alimenta más cobertura de crisis.**

Esto no implica que los medios inventen la realidad. Los períodos de mayor ratio de crisis en titulares (2019, 2023) coincidieron con tensiones sociales y económicas reales. Pero la *magnitud* y la *velocidad* del deterioro perceptual — especialmente el colapso de 2015 con PIB positivo, y el mantenimiento de alta "decadencia" en el CEP pese a la recuperación del IPEC post-2022 — sugieren que la narrativa mediática tiene un efecto multiplicador que va más allá de la descripción de los hechos.

**La brecha entre la realidad económica medible y la percepción ciudadana no es solo un fenómeno de ignorancia o sesgo cognitivo individual. Es, en parte, un producto de cómo se construye y amplifica la narrativa colectiva sobre el estado del país.** Y esa construcción tiene consecuencias: afecta las decisiones de consumo e inversión, moldea las preferencias electorales, y determina qué problemas entran a la agenda pública y cuáles quedan fuera.

Las personas que más dependen del Estado — de la salud pública, la educación, el transporte — son las más expuestas a los efectos de una percepción de crisis sostenida, porque esa percepción desplaza otras prioridades del debate político hacia la gestión de la emergencia permanente.

---

## 12. Próximos pasos

Los resultados de esta investigación abren tres líneas de trabajo:

**Mejora del clasificador de tono.** Reemplazar el clasificador por palabras clave con un modelo de lenguaje natural (BERT en español, o fine-tuning de un modelo existente sobre los titulares ya recolectados con etiquetas manuales). Esto elevaría la sensibilidad desde el 2% actual de clasificación "crisis" a una cifra más realista.

**Expansión del corpus mediático.** Incorporar televisión (transcripciones de noticiarios) y redes sociales (Twitter/X en Chile). Esto permitiría medir si la narrativa de crisis emerge primero en la prensa escrita, en la televisión, o en redes sociales — lo cual tiene implicancias directas sobre el mecanismo causal.

**Análisis de heterogeneidad.** Estudiar si el efecto de la narrativa es diferente por nivel socioeconómico, región, o medio de información preferido. La hipótesis predice que el efecto debería ser mayor en las personas con menor acceso a fuentes de información diversas.

**Publicación de los datos.** Todos los datasets de este proyecto son de fuentes públicas y están disponibles en el repositorio para que otros investigadores puedan replicar, extender o refutar estos hallazgos.

---

*Este documento resume los hallazgos de una investigación ciudadana con datos abiertos, sin financiamiento institucional ni agenda política partidaria. Los análisis son reproducibles a partir del código disponible en el repositorio.*

*Repositorio: github.com/KenaEscobar/la-brecha-narrativa*
