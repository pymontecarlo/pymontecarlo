""""""

# Standard library modules.
import math

# Third party modules.
import pandas as pd
import numpy as np

# Local modules.
from pymontecarlo.formats.series import SeriesBuilder

# Globals and constants variables.


def ensure_distinct_columns(dataframe, tolerances=None):
    if len(dataframe) < 2:
        return dataframe

    if tolerances is None:
        tolerances = {}

    drop_columns = []
    for column in dataframe.columns:
        values = dataframe[column].to_numpy()
        tolerance = tolerances.get(column)

        if tolerance is None or not pd.api.types.is_numeric_dtype(values):
            allequal = all(values[0] == v for v in values)
        else:
            allequal = np.allclose(values, values[0], atol=tolerance)

        if allequal:
            drop_columns.append(column)

    return dataframe.drop(drop_columns, axis=1)


def create_options_dataframe(
    list_options,
    settings,
    only_different_columns=False,
    abbreviate_name=False,
    format_number=False,
):
    """
    Returns a :class:`pandas.DataFrame`.

    If *only_different_columns*, the data rows will only contain the columns
    that are different between the options.
    """
    list_series = []

    for options in list_options:
        builder = SeriesBuilder(settings, abbreviate_name, format_number)
        options.convert_series(builder)

        s = builder.build()
        list_series.append(s)

    df = pd.DataFrame(list_series)

    if not only_different_columns or len(df) < 2:
        return df

    tolerances = builder.gettolerances()

    return ensure_distinct_columns(df, tolerances)


def create_results_dataframe(
    list_results,
    settings,
    result_classes=None,
    abbreviate_name=False,
    format_number=False,
):
    """
    Returns a :class:`pandas.DataFrame`.

    If *result_classes* is a list of :class:`Result`, only the columns from
    this result classes will be returned. If ``None``, the columns from
    all results will be returned.
    """
    list_series = []

    for results in list_results:
        builder = SeriesBuilder(settings, abbreviate_name, format_number)

        for result in results:
            prefix = result.getname().lower() + " "

            if result_classes is None:  # Include all results
                builder.add_entity(result, prefix)

            elif type(result) in result_classes:
                if len(result_classes) == 1:
                    builder.add_entity(result)
                else:
                    builder.add_entity(result, prefix)

        list_series.append(builder.build())

    return pd.DataFrame(list_series)
