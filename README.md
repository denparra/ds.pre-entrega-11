# Pre-entrega M11 — Dashboard de Análisis de Ventas Retail

**Data Science II · CoderHouse** · Pre-entrega del Módulo 11 (visualización de datos y storytelling)

## Dashboard y aviso importante de acceso

**Enlace de entrega:** [Abrir el dashboard de ventas retail](https://datastudio.google.com/s/iyexulgoHJ4).

**Respaldo:** [Ver el dashboard en PDF](docs/dashboard-ventas-retail.pdf). Es
una captura estática del informe y no permite utilizar los filtros interactivos.

> [!IMPORTANT]
> **Se presentaron dificultades para publicar el dashboard con acceso anónimo.**
> Aunque el enlace abre el informe, en las pruebas sin iniciar sesión los gráficos,
> indicadores y algunos controles mostraron «Error del sistema».
>
> **Para revisarlo, inicia sesión con tu cuenta de Google o Gmail y abre el enlace.**
> El informe y sus indicadores se visualizaron desde la cuenta propietaria; el
> acceso con una cuenta distinta **aún no ha sido verificado**, por lo que iniciar
> sesión podría no ser suficiente. Si el problema persiste, solicita acceso al
> responsable de la entrega. La carga anónima requerida por la consigna permanece
> sin resolver.

### Elección de herramienta y dificultades de publicación

La herramienta con la que tenía mayor experiencia era Power BI. Durante la
preparación de esta entrega solo contaba con la versión gratuita y encontré
limitaciones para compartir el informe en las condiciones disponibles; no contaba
con una licencia Pro. Por familiaridad con el ecosistema de Google y facilidad de
acceso, opté por Looker Studio y conecté el CSV preparado.

## Tabla de contenidos

1. [Resumen ejecutivo](#resumen-ejecutivo)
2. [La pregunta de negocio](#la-pregunta-de-negocio)
3. [Dataset](#dataset)
4. [Cómo reproducir el extracto](#cómo-reproducir-el-extracto)
5. [Hallazgos](#hallazgos)
6. [Mapa de trazabilidad: rúbrica ↔ evidencia](#mapa-de-trazabilidad-rúbrica--evidencia)
7. [Estructura del repositorio](#estructura-del-repositorio)
8. [Reproducibilidad y versiones](#reproducibilidad-y-versiones)
9. [Solución de problemas](#solución-de-problemas)
10. [Referencias](#referencias)

## Resumen ejecutivo

| Ítem | Valor |
|---|---|
| Herramienta | Looker Studio, con fuente CSV cargada en el informe |
| Dataset | Sample Superstore — 9.994 líneas de pedido, 5.009 pedidos, 2015-2018 |
| Usuario del tablero | Gerencia Comercial |
| Pregunta de negocio | ¿Qué categorías impulsan el crecimiento y cuánto margen aportan? |
| Visualizaciones | 4 gráficos y 4 tarjetas de indicadores |
| Hallazgo principal | Las ventas crecen **+20,4 %** en 2018 con el margen estancado en **12,5 %** |
| Caso a revisar | Furniture: **32,3 %** de las ventas y **6,4 %** de la utilidad total |
| Patrón observado | Los grupos con descuentos superiores al 20 % presentan margen agregado negativo |

El tablero responde una sola pregunta y la responde de lo general a lo específico:
cuánto se vendió, cómo evolucionó, qué categoría lo explica y dónde ocurre.

## La pregunta de negocio

**Usuario:** Gerencia Comercial de una cadena de retail.

**Problema:** la facturación crece, pero la utilidad no acompaña. La gerencia no
tiene una lectura única que cruce crecimiento, categoría y rentabilidad.

**Pregunta:** *¿Qué categorías están impulsando el crecimiento y cuánto margen
aporta cada una?*

**Decisión que habilita:** dónde poner el esfuerzo comercial del próximo
trimestre y qué política de descuentos aplicar.

## Qué muestra el dashboard

El informe presenta cuatro indicadores: ventas de 2018 (**733.215,26**), margen
global (**12,47 %**), ticket promedio (**458,61**) y margen de Q4 2018
(**9,80 %**). Los importes se contrastaron con el CSV; los cuatro indicadores se
observaron también en la sesión de edición de la cuenta propietaria.

Debajo de los indicadores se presentan cuatro vistas: evolución de las ventas,
comparación por categoría, distribución por estado y relación entre ventas y
rentabilidad por subcategoría. El informe incluye controles de periodo, región y
categoría. Los filtros de región, categoría y periodo se probaron previamente en
la sesión de edición; su funcionamiento para visitantes sigue pendiente debido al
error de acceso. El PDF ofrece una vista estática del informe.

## Dataset

- **Nombre:** Sample Superstore (el dataset de demostración de Tableau).
- **Archivo original:** `data/raw/sample-superstore.csv` — incluido en el repo,
  así que no hace falta descargar nada.
- **Archivo que consume el tablero:** `data/dashboard_ventas.csv` — 9.994 filas ×
  21 columnas, UTF-8, sin valores nulos.
- **Grano:** una línea de pedido (un producto dentro de un pedido).
- **Periodo:** 2015-01-03 a 2018-12-30.
- **Cobertura:** Estados Unidos, 49 estados, 531 ciudades, 3 categorías y 17
  sub-categorías.

| Campo | Rol | Descripción |
|---|---|---|
| `Order Date`, `Year`, `Quarter`, `YearMonth` | Dimensión temporal | Cuándo ocurrió la venta |
| `Category`, `Sub-Category` | Dimensión | Qué se vendió |
| `State`, `City`, `Region` | Dimensión geográfica | Dónde se vendió |
| `Segment`, `Ship Mode` | Dimensión | A quién y cómo se envió |
| `Sales`, `Profit`, `Quantity`, `Discount` | Medida | Cuánto, con qué margen y con qué descuento |

**Limpieza aplicada:** el archivo original trae 806 filas corruptas al final
(columnas desplazadas, sin fecha ni métricas). Se descartan y se reporta el
conteo al ejecutar el script. Quedan las 9.994 filas válidas.

## Cómo reproducir el extracto

**Requisitos:** Python 3.11+ y Git.

```powershell
git clone <url-del-repositorio>
cd pre-entregamd11
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.prep_dashboard
```

En macOS o Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m src.prep_dashboard
```

Salida esperada:

```text
Filas descartadas por no tener fecha o ventas validas: 806
Filas en el archivo original: 10800
Filas validas exportadas: 9994
Pedidos unicos: 5009
Ventas totales: $2,297,200.86
Margen global: 12.47%
Periodo: 2015-01-03 a 2018-12-30
```

El script es idempotente: se puede correr las veces que haga falta y siempre
produce el mismo `data/dashboard_ventas.csv`.

## Hallazgos

### El crecimiento es real, el margen no acompaña

| Año | Ventas | Margen | Variación |
|---|---:|---:|---:|
| 2015 | $484.247,50 | 10,23 % | — |
| 2016 | $470.532,51 | 13,10 % | −2,83 % |
| 2017 | $609.205,60 | 13,43 % | +29,47 % |
| 2018 | $733.215,26 | 12,74 % | **+20,36 %** |

### El cuarto trimestre es el que más vende y el que menos deja

Q4 acumula el **38,22 %** de las ventas de los cuatro años. Pero Q4 2018 vendió
18,62 % más que Q4 2017 y dejó **6,35 puntos porcentuales menos de margen**
(9,80 % contra 16,15 %).

### Furniture vende mucho y aporta poco

| Categoría | Ventas | % de ventas | Margen |
|---|---:|---:|---:|
| Technology | $836.154,03 | 36,4 % | 17,40 % |
| Furniture | $741.999,80 | 32,3 % | **2,49 %** |
| Office Supplies | $719.047,03 | 31,3 % | 17,04 % |

**Tables** sola vende $206.965 y pierde $17.725 (margen −8,56 %).

### El mecanismo es el descuento

| Descuento | Margen resultante |
|---|---:|
| 0 % | 29,51 % |
| 11–20 % | 11,58 % |
| 21–30 % | **−10,05 %** |
| 31–50 % | **−24,80 %** |

En los grupos de descuento superiores al 20 %, el margen agregado es negativo;
esta asociación no demuestra causalidad. Hay **10 estados con
margen negativo**, entre ellos Texas (tercer mercado del país, margen −15,12 %).

## Mapa de trazabilidad: rúbrica ↔ evidencia

| # | Criterio de la consigna | Evidencia en el repo | Estado |
|---|---|---|---|
| 1 | El enlace es accesible y el dashboard carga | Enlace al inicio de este README | **No cumple en la prueba anónima**; otra cuenta pendiente |
| 2 | ≥3 tipos de gráficos distintos y relevantes | Cuatro gráficos en el informe | Construidos; coordinación pública pendiente de verificar |
| 3 | Lectura de lo general a lo específico | Indicadores y cuatro vistas | Estructura presente |
| 4 | Títulos descriptivos | Títulos de los cuatro gráficos | Presentes |
| 5 | Paleta consistente sin saturar | Diseño del informe | Revisión visual pública pendiente |

## Estructura del repositorio

```text
pre-entregamd11/
├── README.md                       # este documento
├── consignamd11.md                 # consigna original de la actividad
├── requirements.txt                # dependencias del preparador
├── .gitignore
├── data/
│   ├── raw/sample-superstore.csv   # dataset original (10.800 filas)
│   └── dashboard_ventas.csv        # extracto limpio (9.994 × 21, UTF-8)
├── src/
│   ├── prep_dashboard.py           # limpieza + columnas de tiempo → extracto
│   └── render_wireframe.py         # wireframe de referencia (opcional)
└── docs/
    └── dashboard-ventas-retail.pdf  # exportación estática del informe
```

## Reproducibilidad y versiones

- El extracto se regenera con un comando y siempre da el mismo resultado: no hay
  aleatoriedad involucrada.
- `data/raw/` está versionado, así que el repositorio es autocontenido.
- El margen se calcula con `SUM(Profit) / SUM(Sales)`, porque promediar
  porcentajes por línea da un número distinto.
- Rango de versiones en `requirements.txt`: pandas ≥2,2,<3. matplotlib es
  opcional y solo se usa para el wireframe.

## Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `ModuleNotFoundError: No module named 'pandas'` | El intérprete no es el del `.venv` | Activar el venv (comandos de la sección 4) |
| `ValueError: Al archivo original le faltan columnas requeridas` | Se pasó otro CSV como entrada | Usar `data/raw/sample-superstore.csv` |
| `Invalid characters in the file` al subir el CSV | El archivo no está en UTF-8 | Regenerarlo con `py -m src.prep_dashboard` |
| El mapa muestra estados en gris | `State` sin tipo Geo, o falta el país en el gráfico | Tipo `Geo → Country subdivision (1st level)` + `Zoom area → Country → United States` |
| La serie temporal apila los eneros de todos los años | Granularidad de `Order Date` en `Date` | Cambiar la pastilla de `Order Date` a `Month` |
| El margen no coincide con este README | Se promedió `Profit / Sales` por línea | Usar `SUM(Profit) / SUM(Sales)` |
| Los controles no filtran todos los gráficos | Hay más de una fuente de datos en el informe | Dejar todo sobre la misma fuente |
| El informe abre, pero las visualizaciones muestran «Error del sistema» | Causa exacta no confirmada; ocurre en pruebas sin sesión | Intentar con una cuenta de Google y solicitar acceso si persiste; no se ha validado con otra cuenta |

## Referencias

- Consigna: [`consignamd11.md`](consignamd11.md).
- Dataset: Sample Superstore — el dataset clásico de demostración de BI.
- Herramienta: [Looker Studio](https://lookerstudio.google.com).
- Documentación oficial: [Crear un informe](https://docs.cloud.google.com/data-studio/create-a-report) · [Subir archivos CSV](https://docs.cloud.google.com/data-studio/upload-csv-files) · [Controles](https://docs.cloud.google.com/data-studio/about-controls) · [Cross-filtering](https://docs.cloud.google.com/data-studio/chart-cross-filtering) · [Tipos geográficos](https://docs.cloud.google.com/data-studio/geo-dimension-reference) · [Líneas de referencia](https://docs.cloud.google.com/data-studio/add-reference-lines-and-reference-bands-to-charts) · [Obtener el link](https://docs.cloud.google.com/data-studio/get-a-link-to-your-report) · [Insertar un informe](https://docs.cloud.google.com/data-studio/embed-a-report).
- Principios de visualización aplicados: jerarquía visual, relación dato-tinta y evitación de gráficos circulares para más de tres categorías.
