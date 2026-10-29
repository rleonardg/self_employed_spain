import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression

from utilities import (ASSETS, COLORES, DATA_PROCESSED, aplicar_estilo, cargar_datos,
                       sectores_con_stock_minimo)

ANIO = 2022
STOCK_MINIMO = 1000
NIVEL_CONFIANZA = 0.95
SALIDA = ASSETS / 'regresion_lineal.png'
SALIDA_TABLA = DATA_PROCESSED / 'regresion_por_anio.csv'


def ajustar_regresion(x: np.ndarray, y: np.ndarray) -> dict:
    X = x.reshape(-1, 1)
    modelo = LinearRegression().fit(X, y)
    n = len(x)
    residuos = y - modelo.predict(X)
    error_tipico = np.sqrt(np.sum(residuos ** 2) / (n - 2))
    sxx = np.sum((x - x.mean()) ** 2)
    t = modelo.coef_[0] / (error_tipico / np.sqrt(sxx))
    return {
        'modelo': modelo,
        'n': n,
        'pendiente': modelo.coef_[0],
        'ordenada': modelo.intercept_,
        'r2': modelo.score(X, y),
        'p_valor': 2 * stats.t.sf(abs(t), df=n - 2),
        'error_tipico': error_tipico,
        'x_media': x.mean(),
        'sxx': sxx,
    }


def banda_confianza(r: dict, xs: np.ndarray, nivel: float = NIVEL_CONFIANZA):
    t_critico = stats.t.ppf((1 + nivel) / 2, df=r['n'] - 2)
    y_recta = r['modelo'].predict(xs.reshape(-1, 1))
    margen = t_critico * r['error_tipico'] * np.sqrt(
        1 / r['n'] + (xs - r['x_media']) ** 2 / r['sxx'])
    return y_recta, y_recta - margen, y_recta + margen


def punto_equilibrio(r: dict) -> float:
    return r['ordenada'] / (1 - r['pendiente'])


def regresion_por_anio(datos: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for anio, grupo in datos.groupby('anio'):
        r = ajustar_regresion(grupo['t_nacimientos'].to_numpy(), grupo['t_muertes'].to_numpy())
        filas.append({'anio': anio, 'n_sectores': r['n'], 'pendiente': r['pendiente'],
                      'ordenada': r['ordenada'], 'r2': r['r2'], 'p_valor': r['p_valor'],
                      'equilibrio_t_nacimientos': punto_equilibrio(r)})
    return pd.DataFrame(filas)


def texto_p(p: float) -> str:
    return 'p < 0.001' if p < 0.001 else f'p = {p:.3f}'


def dibujar(datos: pd.DataFrame, r: dict, anio: int):
    x = datos['t_nacimientos'].to_numpy()
    y = datos['t_muertes'].to_numpy()
    x_media, y_media = x.mean(), y.mean()

    fig, ax = plt.subplots(figsize=(9, 6.4))
    fig.subplots_adjust(left=0.085, right=0.975, top=0.975, bottom=0.105)
    ax.set_xlim(0, np.ceil(x.max() + 1.5))
    ax.set_ylim(0, np.ceil(y.max() + 2))
    ax.grid(True, zorder=0)
    ax.tick_params(length=0, labelsize=9.5)

    xs = np.linspace(x.min(), x.max(), 200)
    y_recta, inferior, superior = banda_confianza(r, xs)
    ax.fill_between(xs, inferior, superior, color=COLORES['serie'], alpha=0.13, lw=0, zorder=2)
    ax.plot(xs, y_recta, color=COLORES['serie_oscura'], lw=2, solid_capstyle='round', zorder=3)
    ax.scatter(x, y, s=52, color=COLORES['serie'], edgecolor=COLORES['superficie'],
               linewidth=1.3, zorder=4)

    guia = dict(color=COLORES['texto_secundario'], lw=1, ls=(0, (3, 3)), zorder=1.5)
    ax.plot([x_media, x_media], [0, y_media], **guia)
    ax.plot([0, x_media], [y_media, y_media], **guia)
    ax.scatter([x_media], [y_media], s=110, marker='D', color=COLORES['texto'],
               edgecolor=COLORES['superficie'], linewidth=1.6, zorder=6)
    ax.annotate(f'Media ({x_media:.1f} %, {y_media:.1f} %)', xy=(x_media, y_media),
                xytext=(x_media + 4.5, y_media - 5.2), ha='left', va='center', fontsize=10,
                fontweight='bold', color=COLORES['texto'], zorder=7,
                arrowprops=dict(arrowstyle='-', color=COLORES['texto_secundario'], lw=0.9,
                                shrinkA=4, shrinkB=7),
                bbox=dict(boxstyle='square,pad=0.2', fc=COLORES['superficie'], ec='none'))

    ax.set_xlabel(f'Tasa de nacimientos {anio} (%)', fontsize=10.5, labelpad=8)
    ax.set_ylabel(f'Tasa de muertes {anio} (%)', fontsize=10.5, labelpad=8)
    return fig


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--mostrar', action='store_true', help='abre la figura en una ventana')
    args = parser.parse_args()

    largo = cargar_datos()
    sectores = sectores_con_stock_minimo(largo, STOCK_MINIMO)
    datos = largo[largo['actividad'].isin(sectores)].dropna(subset=['t_nacimientos', 't_muertes'])

    tabla = regresion_por_anio(datos).round(
        {'pendiente': 4, 'ordenada': 4, 'r2': 4, 'equilibrio_t_nacimientos': 2})
    SALIDA_TABLA.parent.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(SALIDA_TABLA, index=False)
    print('Regresión tasa_muertes ~ tasa_nacimientos por año:')
    print(tabla.to_string(index=False, formatters={'p_valor': '{:.1e}'.format}))

    datos_anio = datos[datos['anio'] == ANIO]
    x = datos_anio['t_nacimientos'].to_numpy()
    y = datos_anio['t_muertes'].to_numpy()
    r = ajustar_regresion(x, y)
    print(f'\n{ANIO}: muertes = {r["ordenada"]:.2f} + {r["pendiente"]:.3f} × nacimientos | '
          f'R² = {r["r2"]:.3f} | {texto_p(r["p_valor"])} | n = {r["n"]} | '
          f'media = ({x.mean():.2f}, {y.mean():.2f}) | equilibrio = {punto_equilibrio(r):.2f} %')

    aplicar_estilo()
    fig = dibujar(datos_anio, r, ANIO)
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(SALIDA)
    print(f'Guardado: {SALIDA}')
    print(f'Guardado: {SALIDA_TABLA}')
    if args.mostrar:
        plt.show()
    plt.close(fig)


if __name__ == '__main__':
    main()
