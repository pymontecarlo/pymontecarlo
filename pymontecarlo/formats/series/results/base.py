""""""

# Standard library modules.

# Third party modules.
import pandas as pd

# Local modules.
from pymontecarlo.formats.series.base import \
    SeriesHandler, find_convert_serieshandler, update_with_prefix
from pymontecarlo.exceptions import ConvertError

# Globals and constants variables.

def create_results_dataframe(list_results, result_classes=None):
    """
    Returns a :class:`pandas.DataFrame`.
    
    If *result_classes* is a list of :class:`Result`, only the columns from
    this result classes will be returned. If ``None``, the columns from 
    all results will be returned.
    """
    list_series = []

    for results in list_results:
        s = pd.Series()

        for result in results:
            try:
                handler = find_convert_serieshandler(result)
            except ConvertError:
                continue

            prefix = result.getname().lower() + ' '
            s_result = handler.convert(result)

            if result_classes is None: # Include all results
                s_result = update_with_prefix(s_result, prefix)
                s = s.append(s_result)

            elif type(result) in result_classes:
                if len(result_classes) == 1:
                    s = s.append(s_result)
                else:
                    s_result = update_with_prefix(s_result, prefix)
                    s = s.append(s_result)

        list_series.append(s)

    return pd.DataFrame(list_series)

class ResultSeriesHandler(SeriesHandler):
    pass
