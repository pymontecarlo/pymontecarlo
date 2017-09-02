""""""

# Standard library modules.

# Third party modules.
import pandas as pd

# Local modules.
from pymontecarlo.formats.series.base import SeriesHandler, SeriesBuilder
from pymontecarlo.exceptions import ConvertError

# Globals and constants variables.

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
        builder = SeriesBuilder(settings)

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

        list_series.append(builder.build(abbreviate_name, format_number))

    return pd.DataFrame(list_series)

class ResultSeriesHandler(SeriesHandler):
    pass
