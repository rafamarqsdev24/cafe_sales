"""
Módulo destinado para carregar as base de dados
"""

import pandas as pd


def load_raw_sales(file: str) -> pd.DataFrame:
    """Recebe um CSV bruto e retorna um DataFrame com as colunas já padronizadas
    Args:
        file: o arquivo CSV em formato de string
    Returns:
        pd.DataFrame: um DataFrame já com as colunas no padrão snake_case
    """
    df = pd.read_csv(f'../data/raw/{file}.csv')
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    return df