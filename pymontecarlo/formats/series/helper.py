""""""

# Standard library modules.
import math

# Third party modules.
import pandas as pd

# Local modules.
from pymontecarlo.formats.series.options.options import OptionsSeriesHandler
from pymontecarlo.formats.series.builder import SeriesBuilder
from pymontecarlo.exceptions import ConvertError

# Globals and constants variables.

def ensure_distinc_columns(dataframe, tolerances=None):
    if len(dataframe) < 2:
        return dataframe

    if tolerances is None:
        tolerances = {}

    drop_columns = []
    for column in dataframe.columns:
        values = dataframe[column].values
        tolerance = tolerances.get(column)

        if tolerance is None:
            allequal = all(values[0] == v for v in values)
        else:
            allequal = all(math.isclose(values[0], v, abs_tol=tolerance) for v in values)

        if allequal:
            drop_columns.append(column)

    return dataframe.drop(drop_columns, axis=1)

def create_options_dataframe(list_options, settings,
                             only_different_columns=False,
                             abbreviate_name=False,
                             format_number=False):
    """
    Returns a :class:`pandas.DataFrame`.
    
    If *only_different_columns*, the data rows will only contain the columns
    that are different between the options.
    """
    list_series = []

    handler = OptionsSeriesHandler(settings)
    for options in list_options:
        s = handler.convert(options, abbreviate_name, format_number)
        list_series.append(s)

    df = pd.DataFrame(list_series)

    if not only_different_columns or len(df) < 2:
        return df

    builder = handler.create_builder(options)
    builder.abbreviate_name = abbreviate_name
    builder.format_number = format_number
    tolerances = builder.gettolerances()

    return ensure_distinc_columns(df, tolerances)

def create_results_dataframe(list_results, settings,
                             result_classes=None,
                             abbreviate_name=False,
                             format_number=False):
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
            prefix = result.getname().lower() + ' '

            try:
                if result_classes is None: # Include all results
                    builder.add_object(result, prefix)

                elif type(result) in result_classes:
                    if len(result_classes) == 1:
                        builder.add_object(result)
                    else:
                        builder.add_object(result, prefix)
            except ConvertError:
                continue

        list_series.append(builder.build())

    return pd.DataFrame(list_series)