""""""

# Standard library modules.

# Third party modules.
import pandas as pd

# Local modules.
from pymontecarlo.formats.series.base import ensure_distinc_columns
from pymontecarlo.formats.series.options.options import OptionsSeriesHandler

# Globals and constants variables.

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

    _s, tolerances = handler.convert(options, abbreviate_name, format_number, return_tolerances=True)

    return ensure_distinc_columns(df, tolerances)
