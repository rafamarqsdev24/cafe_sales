"""
Módulo destinado a funções para diagnóstico referente a limpeza de dados
"""

import pandas as pd


def calculate_df(df: pd.DataFrame, column_name: str, aggregation: pd.Series) -> pd.DataFrame:
    """
    Recebe o DataFrame bruto para calcular o o total e percentual agregado.
    Args:
        df: DataFrame bruto
        column_name: coluna a ser agregada
        aggregation: cálculo a ser feito

    Returns:
        pd.DataFrame: retorna um novo DataFrame com uma coluna agregada e seu percentual
    """

    return pd.DataFrame(
        {
            column_name: aggregation,
            '%': (aggregation / len(df) * 100).round(2),
        }
    ).sort_values(column_name, ascending=False)


def dirty_mask(df: pd.DataFrame) -> pd.DataFrame:
    """Recebe um DataFrame e retorna uma máscara booleana que verifica se há valores sujos ou não.
    Args:
        df: DataFrame em que o filtro será aplicado 
    Returns: Máscara booleana que funcionará de filtro
    """
    
    DIRTY_TOKENS = ['ERROR', 'UNKNOWN']

    return df.isna() | df.isin(DIRTY_TOKENS)