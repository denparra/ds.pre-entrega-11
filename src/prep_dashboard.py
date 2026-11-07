"""Prepara el extracto de ventas retail que consume el dashboard de Looker Studio.

El dashboard no calcula nada desde el CSV crudo: este script deja un extracto
plano, con tipos correctos y columnas de tiempo listas para usar como
dimensiones. Todo lo agregado (ventas por categoria, margen, trimestres) lo
resuelve la herramienta de BI, para que el tablero siga siendo interactivo.

Uso:
    py -m src.prep_dashboard
"""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_PATH = PROJECT_ROOT / "data" / "raw" / "sample-superstore.csv"
DEFAULT_OUT_PATH = PROJECT_ROOT / "data" / "dashboard_ventas.csv"

# Columnas que debe traer el archivo original de Sample Superstore.
REQUIRED_COLUMNS = [
    "Order ID",
    "Order Date",
    "Ship Date",
    "Ship Mode",
    "Segment",
    "Region",
    "State",
    "City",
    "Category",
    "Sub-Category",
    "Product Name",
    "Sales",
    "Quantity",
    "Discount",
    "Profit",
]

# Columnas que se conservan en el extracto final, en este orden.
OUTPUT_COLUMNS = REQUIRED_COLUMNS + [
    "Year",
    "Quarter",
    "QuarterLabel",
    "Month",
    "MonthName",
    "YearMonth",
]

# Nombres de mes en ingles, porque el locale del entorno no siempre esta en espanol.
MONTH_NAMES = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}


def cargar_crudo(ruta_datos: Path = DEFAULT_RAW_PATH) -> pd.DataFrame:
    """Lee el CSV original y valida que esten las columnas esperadas."""
    datos = pd.read_csv(ruta_datos, encoding="utf-8-sig")
    faltantes = set(REQUIRED_COLUMNS) - set(datos.columns)
    if faltantes:
        raise ValueError(
            "Al archivo original le faltan columnas requeridas: "
            + ", ".join(sorted(faltantes))
        )
    return datos


def limpiar(datos: pd.DataFrame) -> pd.DataFrame:
    """Descarta las filas sin fecha de pedido ni ventas.

    La copia publica del dataset trae una cola de filas corruptas al final del
    archivo: son 806 registros con las columnas desplazadas, sin fecha ni
    metricas. Se eliminan porque no representan ninguna venta.
    """
    fechas = pd.to_datetime(datos["Order Date"], format="%m/%d/%Y", errors="coerce")
    ventas = pd.to_numeric(datos["Sales"], errors="coerce")

    filas_invalidas = fechas.isna() | ventas.isna()
    if filas_invalidas.any():
        print(f"Filas descartadas por no tener fecha o ventas validas: {filas_invalidas.sum()}")

    limpio = datos.loc[~filas_invalidas].copy()
    limpio["Order Date"] = fechas[~filas_invalidas]
    limpio["Ship Date"] = pd.to_datetime(
        limpio["Ship Date"], format="%m/%d/%Y", errors="coerce"
    )

    for columna in ["Sales", "Quantity", "Discount", "Profit"]:
        limpio[columna] = pd.to_numeric(limpio[columna], errors="coerce")

    # Sin metricas no hay nada que graficar: se descartan los faltantes restantes.
    limpio = limpio.dropna(subset=["Sales", "Profit", "Quantity", "Discount"])
    return limpio


def enriquecer(datos: pd.DataFrame) -> pd.DataFrame:
    """Agrega las columnas de tiempo que el tablero usara como dimensiones."""
    enriquecido = datos.copy()
    fecha = enriquecido["Order Date"]

    enriquecido["Year"] = fecha.dt.year
    enriquecido["Quarter"] = fecha.dt.quarter
    enriquecido["QuarterLabel"] = (
        "Q" + enriquecido["Quarter"].astype(str) + " " + enriquecido["Year"].astype(str)
    )
    enriquecido["Month"] = fecha.dt.month
    enriquecido["MonthName"] = fecha.dt.month.map(MONTH_NAMES)
    enriquecido["YearMonth"] = fecha.dt.strftime("%Y-%m")
    return enriquecido


def exportar(datos: pd.DataFrame, ruta_salida: Path = DEFAULT_OUT_PATH) -> Path:
    """Guarda el extracto en UTF-8, sin indice y solo con las columnas finales."""
    ruta_salida = Path(ruta_salida)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    datos[OUTPUT_COLUMNS].to_csv(ruta_salida, index=False, encoding="utf-8")
    return ruta_salida


def preparar(
    ruta_datos: Path = DEFAULT_RAW_PATH,
    ruta_salida: Path = DEFAULT_OUT_PATH,
) -> dict[str, object]:
    """Encadena carga, limpieza, enriquecimiento y exportacion."""
    crudo = cargar_crudo(ruta_datos)
    limpio = limpiar(crudo)
    enriquecido = enriquecer(limpio)
    ruta = exportar(enriquecido, ruta_salida)
    return {
        "filas_crudas": len(crudo),
        "filas_validas": len(enriquecido),
        "pedidos": int(enriquecido["Order ID"].nunique()),
        "ventas_totales": float(enriquecido["Sales"].sum()),
        "margen_global": float(enriquecido["Profit"].sum() / enriquecido["Sales"].sum()),
        "desde": enriquecido["Order Date"].min(),
        "hasta": enriquecido["Order Date"].max(),
        "ruta": ruta,
    }


def main() -> None:
    resultado = preparar()
    print(f"Filas en el archivo original: {resultado['filas_crudas']}")
    print(f"Filas validas exportadas: {resultado['filas_validas']}")
    print(f"Pedidos unicos: {resultado['pedidos']}")
    print(f"Ventas totales: ${resultado['ventas_totales']:,.2f}")
    print(f"Margen global: {resultado['margen_global']:.2%}")
    print(f"Periodo: {resultado['desde']:%Y-%m-%d} a {resultado['hasta']:%Y-%m-%d}")
    print(f"Extracto exportado en: {resultado['ruta']}")


if __name__ == "__main__":
    main()
