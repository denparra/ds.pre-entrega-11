"""Genera el wireframe de referencia del dashboard a partir del extracto limpio.

No forma parte del entregable: es una guia de diseno para construir el tablero
en Looker Studio. Se ejecuta aparte porque requiere matplotlib, que no es una
dependencia del preparador de datos.

Uso:
    py -m src.render_wireframe
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "dashboard_ventas.csv"
DEFAULT_OUT_PATH = PROJECT_ROOT / "docs" / "img" / "wireframe-dashboard.png"

INK = "#1F2933"
MUTED = "#64748B"
GRID = "#E2E8F0"
CARD = "#F8FAFC"
BORDER = "#CBD5E1"
ACCENT = "#0F766E"
ALERT = "#B91C1C"

# Los montos se escriben a mano, no dentro de cadenas con $, para que
# matplotlib no los interprete como formulas.
plt.rcParams["text.parse_math"] = False


def fmt_usd(valor: float, decimales: int = 0) -> str:
    """Formatea un monto con separador de miles y coma decimal."""
    texto = f"{valor:,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "$" + texto


def fmt_porcentaje(valor: float, decimales: int = 1) -> str:
    """Formatea una proporcion como porcentaje con coma decimal."""
    return f"{valor * 100:.{decimales}f}%".replace(".", ",")


def fmt_puntos(valor: float) -> str:
    """Formatea una diferencia en puntos porcentuales con signo."""
    return f"{valor:+.1f} pp".replace(".", ",")


def tarjeta_kpi(eje, etiqueta: str, valor: str, detalle: str, destacada: bool = False) -> None:
    """Dibuja una tarjeta de indicador con su etiqueta y su variacion."""
    eje.set_axis_off()
    eje.set_xlim(0, 1)
    eje.set_ylim(0, 1)

    borde = ALERT if destacada else BORDER
    fondo = "#FEF2F2" if destacada else CARD
    eje.add_patch(
        FancyBboxPatch(
            (0.02, 0.04),
            0.96,
            0.92,
            boxstyle="round,pad=0.01,rounding_size=0.04",
            linewidth=1.2,
            edgecolor=borde,
            facecolor=fondo,
        )
    )
    eje.text(0.07, 0.78, etiqueta.upper(), fontsize=8.5, color=MUTED, va="center")
    eje.text(0.07, 0.47, valor, fontsize=21, color=ALERT if destacada else INK, va="center")
    eje.text(0.07, 0.18, detalle, fontsize=8.5, color=MUTED, va="center")


def panel(eje, titulo: str, subtitulo: str) -> None:
    """Enmarca un panel con su titulo descriptivo y su bajada."""
    eje.set_axis_off()
    eje.set_xlim(0, 1)
    eje.set_ylim(0, 1)
    eje.add_patch(
        FancyBboxPatch(
            (0.005, 0.005),
            0.99,
            0.99,
            boxstyle="round,pad=0.005,rounding_size=0.015",
            linewidth=1.0,
            edgecolor=BORDER,
            facecolor="white",
        )
    )
    eje.text(0.03, 0.93, titulo, fontsize=11, color=INK, weight="bold", va="center")
    eje.text(0.03, 0.855, subtitulo, fontsize=8.5, color=MUTED, va="center")


def dibujar(datos: pd.DataFrame, ruta_salida: Path = DEFAULT_OUT_PATH) -> Path:
    """Compone el tablero de referencia y guarda la imagen."""
    ventas_2018 = datos.loc[datos["Year"] == 2018, "Sales"].sum()
    ventas_2017 = datos.loc[datos["Year"] == 2017, "Sales"].sum()
    variacion = ventas_2018 / ventas_2017 - 1
    ventas_totales = datos["Sales"].sum()
    margen_global = datos["Profit"].sum() / ventas_totales
    pedidos = datos["Order ID"].nunique()
    ticket = ventas_totales / pedidos

    q4_2018 = datos.loc[datos["QuarterLabel"] == "Q4 2018"]
    q4_2017 = datos.loc[datos["QuarterLabel"] == "Q4 2017"]
    margen_q4_2018 = q4_2018["Profit"].sum() / q4_2018["Sales"].sum()
    margen_q4_2017 = q4_2017["Profit"].sum() / q4_2017["Sales"].sum()
    delta_pp = (margen_q4_2018 - margen_q4_2017) * 100

    fig = plt.figure(figsize=(16, 9), dpi=100, facecolor="white")

    fig.text(
        0.03,
        0.955,
        "¿Qué categorías impulsan el crecimiento y cuánto margen aportan?",
        fontsize=17,
        color=INK,
        weight="bold",
        va="center",
    )
    fig.text(
        0.03,
        0.915,
        f"Gerencia Comercial · Ventas retail 2015-2018 · {len(datos):,} líneas de pedido, "
        f"{pedidos:,} pedidos".replace(",", "."),
        fontsize=9.5,
        color=MUTED,
        va="center",
    )

    # Fila 1: indicadores.
    tarjetas = [
        ("Ventas 2018", fmt_usd(ventas_2018), f"+{fmt_porcentaje(variacion)} frente a 2017"),
        ("Margen global", fmt_porcentaje(margen_global), f"sobre {fmt_usd(ventas_totales / 1e6, 2)}M vendidos"),
        ("Ticket promedio", fmt_usd(ticket, 2), f"{pedidos:,} pedidos".replace(",", ".")),
        ("Margen Q4 2018", fmt_porcentaje(margen_q4_2018), f"{fmt_puntos(delta_pp)} frente a Q4 2017"),
    ]
    ancho = (0.95 - 3 * 0.012) / 4
    for indice, (etiqueta, valor, detalle) in enumerate(tarjetas):
        eje = fig.add_axes([0.03 + indice * (ancho + 0.012), 0.755, ancho, 0.13])
        tarjeta_kpi(eje, etiqueta, valor, detalle, destacada=(indice == 3))

    # Fila 2 izquierda: serie temporal de ventas mensuales.
    eje_serie = fig.add_axes([0.03, 0.42, 0.60, 0.30])
    panel(
        eje_serie,
        "Las ventas crecen año tras año y se concentran en el cuarto trimestre",
        "Serie mensual · ventas netas",
    )
    eje_serie.set_xlim(0, 1)
    eje_serie.set_ylim(0, 1)
    serie = (
        datos.groupby("YearMonth")["Sales"]
        .sum()
        .rename_axis("mes")
        .reset_index()
        .sort_values("mes")
    )
    valores = serie["Sales"].to_numpy()
    xs = [0.06 + i * (0.90 / (len(valores) - 1)) for i in range(len(valores))]
    base = 0.18
    ys = [base + (valor / valores.max()) * 0.62 for valor in valores]
    eje_serie.plot(xs, ys, color=ACCENT, linewidth=2.0, solid_capstyle="round")
    eje_serie.fill_between(xs, [base] * len(xs), ys, color=ACCENT, alpha=0.12)
    eje_serie.plot([0.06, 0.96], [base, base], color=GRID, linewidth=1.0)
    eje_serie.text(0.055, base + 0.05, "ventas ($)", fontsize=7.5, color=MUTED, rotation=90, va="bottom")
    for posicion, etiqueta in [(0, "2015"), (12, "2016"), (24, "2017"), (36, "2018")]:
        eje_serie.plot([xs[posicion], xs[posicion]], [base - 0.05, base], color=MUTED, linewidth=0.8)
        eje_serie.text(xs[posicion], 0.09, etiqueta, fontsize=8.5, color=MUTED, ha="center")
    pico = int(valores.argmax())
    eje_serie.annotate(
        "pico de Q4",
        xy=(xs[pico], ys[pico]),
        xytext=(xs[pico] - 0.18, ys[pico] + 0.06),
        fontsize=8.5,
        color=ALERT,
        arrowprops={"arrowstyle": "-", "color": ALERT, "linewidth": 0.9},
    )

    # Fila 2 derecha: ranking de categorias.
    eje_barras = fig.add_axes([0.665, 0.42, 0.315, 0.30])
    panel(
        eje_barras,
        "Furniture vende un tercio del total y aporta 6% del margen",
        "Ventas por categoría · etiqueta con margen",
    )
    eje_barras.set_xlim(0, 1)
    eje_barras.set_ylim(0, 1)
    por_categoria = (
        datos.groupby("Category")
        .agg(ventas=("Sales", "sum"), margen=("Profit", "sum"))
        .sort_values("ventas", ascending=False)
    )
    tope = por_categoria["ventas"].max()
    for indice, (categoria, fila) in enumerate(por_categoria.iterrows()):
        y = 0.60 - indice * 0.21
        largo = (fila["ventas"] / tope) * 0.44
        proporcion = fila["margen"] / fila["ventas"]
        eje_barras.add_patch(
            plt.Rectangle(
                (0.30, y),
                largo,
                0.12,
                color=ALERT if proporcion < 0.05 else ACCENT,
                alpha=0.85,
                linewidth=0,
            )
        )
        eje_barras.text(0.29, y + 0.06, categoria, fontsize=8.5, color=INK, ha="right", va="center")
        eje_barras.text(
            0.31 + largo,
            y + 0.06,
            f"{fmt_usd(fila['ventas'] / 1e3)}K · {fmt_porcentaje(proporcion)}",
            fontsize=8,
            color=ALERT if proporcion < 0.05 else MUTED,
            va="center",
        )

    # Fila 3 izquierda: mapa (marcador de posicion).
    eje_mapa = fig.add_axes([0.03, 0.10, 0.42, 0.28])
    panel(
        eje_mapa,
        "California y Nueva York concentran un tercio de la facturación",
        "Mapa por estado · ventas netas",
    )
    eje_mapa.set_xlim(0, 1)
    eje_mapa.set_ylim(0, 1)
    eje_mapa.add_patch(
        plt.Rectangle(
            (0.06, 0.14),
            0.88,
            0.56,
            fill=False,
            edgecolor=BORDER,
            linewidth=1.2,
            linestyle=(0, (4, 3)),
        )
    )
    eje_mapa.text(
        0.50,
        0.42,
        "filled map por State\n(Geo chart · Zoom area: United States)",
        fontsize=9,
        color=MUTED,
        ha="center",
        va="center",
    )
    top_estados = datos.groupby("State")["Sales"].sum().sort_values(ascending=False).head(3)
    etiquetas = " · ".join(f"{estado} {fmt_usd(valor / 1e3)}K" for estado, valor in top_estados.items())
    eje_mapa.text(0.06, 0.05, etiquetas, fontsize=7.5, color=MUTED, va="center")

    # Fila 3 derecha: dispersion margen contra volumen.
    eje_disp = fig.add_axes([0.495, 0.10, 0.485, 0.28])
    panel(
        eje_disp,
        "Tables vende $207K y pierde $18K: el descuento se come el margen",
        "Dispersión por sub-categoría · ventas vs margen",
    )
    eje_disp.set_xlim(0, 1)
    eje_disp.set_ylim(0, 1)
    subcategorias = (
        datos.groupby("Sub-Category")
        .agg(ventas=("Sales", "sum"), margen=("Profit", "sum"))
        .assign(ratio=lambda marco: marco["margen"] / marco["ventas"])
    )
    tope_ventas = subcategorias["ventas"].max()
    minimo = subcategorias["ratio"].min()
    maximo_ratio = subcategorias["ratio"].max()

    def altura(ratio: float) -> float:
        """Mapea un margen a la coordenada vertical del panel."""
        return 0.24 + ((ratio - minimo) / (maximo_ratio - minimo)) * 0.52

    eje_disp.plot([0.06, 0.96], [altura(0), altura(0)], color=GRID, linewidth=1.0, linestyle=(0, (3, 3)))
    eje_disp.text(0.095, altura(0) + 0.025, "margen 0%", fontsize=7.5, color=MUTED, ha="left")
    eje_disp.text(0.03, 0.52, "margen %", fontsize=7.5, color=MUTED, rotation=90, va="center")
    eje_disp.text(0.96, 0.09, "ventas ($)", fontsize=7.5, color=MUTED, ha="right")
    for nombre, fila in subcategorias.iterrows():
        x = 0.08 + (fila["ventas"] / tope_ventas) * 0.82
        y = altura(fila["ratio"])
        negativo = fila["ratio"] < 0
        eje_disp.scatter(
            [x], [y], s=70, color=ALERT if negativo else ACCENT, alpha=0.8,
            linewidth=1.4, edgecolor="white", zorder=3,
        )
        if negativo or fila["ventas"] > tope_ventas * 0.40:
            a_la_izquierda = x > 0.82
            eje_disp.annotate(
                nombre,
                xy=(x, y),
                xytext=(-10, -3) if a_la_izquierda else (0, -14 if negativo else 11),
                textcoords="offset points",
                fontsize=7.5,
                color=ALERT if negativo else MUTED,
                ha="right" if a_la_izquierda else "center",
            )

    fig.text(
        0.03,
        0.035,
        "Wireframe de referencia, no el entregable · Controles: rango de fechas, Region, Category · "
        "Clic en una categoría filtra los otros tres paneles",
        fontsize=8,
        color=MUTED,
        va="center",
    )

    ruta_salida = Path(ruta_salida)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta_salida, dpi=100, facecolor="white")
    plt.close(fig)
    return ruta_salida


def main() -> None:
    datos = pd.read_csv(DEFAULT_DATA_PATH)
    ruta = dibujar(datos)
    print(f"Wireframe guardado en: {ruta}")


if __name__ == "__main__":
    main()
