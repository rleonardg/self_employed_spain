from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_RAW = BASE_DIR / 'data' / 'raw'
DATA_PROCESSED = BASE_DIR / 'data' / 'processed'
ANIOS = [2019, 2020, 2021, 2022]


def leer_csv(ruta: str | Path) -> pd.DataFrame:
    df = pd.read_csv(ruta, sep=';', encoding='latin-1', dtype='str')
    df.columns = (df.columns.str.strip()
                  .str.lower()
                  .str.replace(' ', '_')
                  .str.replace('ó', 'o')
                  .str.replace('í', 'i')
                  )
    return df


def numero(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.str.strip().str.replace('.', '', regex=False), errors='coerce')


def por_actividad(df: pd.DataFrame) -> pd.Series:
    return df[(df['actividad_principal_(cnae_2009)'] != 'Todas las actividades')
              & (df['condicion_juridica'] == 'Personas físicas')
              & (df['comunidades_y_ciudades_autonomas'].isna())
              ].set_index('actividad_principal_(cnae_2009)')['total']


def tabla_anual(anio: int) -> pd.DataFrame:
    datos = {}
    for indicador in ['stock', 'nacimientos', 'muertes']:
        df = leer_csv(DATA_RAW / f'{indicador}-{anio}.csv')
        df['total'] = numero(df['total'])
        datos[indicador] = por_actividad(df)
    return pd.DataFrame(datos)


def calcular_tasas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    stock = df['stock'].replace(0, np.nan)
    df['t_nacimientos'] = np.round((df['nacimientos'] / stock) * 100, 2)
    df['t_muertes'] = np.round((df['muertes'] / stock) * 100, 2)
    df['t_neta'] = np.round(df['t_nacimientos'] - df['t_muertes'], 2)
    return df


def formato_largo(tablas: dict[int, pd.DataFrame]) -> pd.DataFrame:
    partes = []
    for anio, tabla in tablas.items():
        parte = tabla.rename_axis('actividad').reset_index()
        parte.insert(0, 'anio', anio)
        partes.append(parte)
    largo = pd.concat(partes, ignore_index=True)
    largo['actividad'] = largo['actividad'].str.replace(r'\s+', ' ', regex=True).str.strip()
    largo.insert(1, 'codigo_cnae', largo['actividad'].str[:2].astype(int))
    return largo


def main() -> None:
    tablas = {anio: calcular_tasas(tabla_anual(anio)) for anio in ANIOS}

    unido = pd.DataFrame({str(anio): tabla['t_neta'] for anio, tabla in tablas.items()})
    largo = formato_largo(tablas)

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    unido.to_excel(DATA_PROCESSED / 'por_sector.xlsx')
    largo.to_csv(DATA_PROCESSED / 'autonomos_por_sector.csv', index=False)

    total = largo.groupby('anio')[['stock', 'nacimientos', 'muertes']].sum()
    total['t_nacimientos'] = (total['nacimientos'] / total['stock'] * 100).round(2)
    total['t_muertes'] = (total['muertes'] / total['stock'] * 100).round(2)
    total['t_neta'] = (total['t_nacimientos'] - total['t_muertes']).round(2)

    print(f'Sectores CNAE: {unido.shape[0]} | años: {", ".join(unido.columns)}')
    print('\nTotal nacional de autónomos (personas físicas):')
    print(total.to_string())
    print(f'\nGuardado: {DATA_PROCESSED / "por_sector.xlsx"}')
    print(f'Guardado: {DATA_PROCESSED / "autonomos_por_sector.csv"}')


if __name__ == '__main__':
    main()
