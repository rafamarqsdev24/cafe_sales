import pandas as pd
import matplotlib.pyplot as plt


def dirty_graphics(df: pd.DataFrame, column_name: str, kind: str, color: str) -> plt.Axes:
    """Recebe um DataFrame e retorna a área de plotagem com um gráfico
    Args:
        df: DataFrame fonte para o gráfico
        column_name: coluna a ser ordenada
        kind: tipo de gráfico
        color: cor dos dados agregados
    Returns:
        plt.Axes: Área de plotagem
    """

    ax = df.sort_values(column_name)[column_name].plot(
        kind=kind,
        figsize=(8, 4),
        color=color,
        edgecolor='white',
    )

    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    return ax
