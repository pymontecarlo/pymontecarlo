""""""

# Standard library modules.

# Third party modules.
import pandas as pd

# Local modules.
from pymontecarlo.formats.series.base import find_convert_serieshandler

# Globals and constants variables.

def create_options_dataframe(list_options, only_different_columns=False):
    """
    Returns a :class:`pandas.DataFrame`.
    
    If *only_different_columns*, the data rows will only contain the columns
    that are different between the options.
    """
    list_series = []

    for options in list_options:
        handler = find_convert_serieshandler(options)
        s = handler.convert(options)
        list_series.append(s)

    df = pd.DataFrame(list_series)

    if not only_different_columns or len(df) < 2:
        return df

    drop_columns = []
    for column in df.columns:
        values = df[column].values
        if all(column.compare(values[0], v) for v in values):
            drop_columns.append(column)

    df = df.drop(drop_columns, axis=1)

    return df