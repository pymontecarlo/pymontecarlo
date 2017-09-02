""""""

# Standard library modules.

# Third party modules.
import pandas as pd

# Local modules.
from pymontecarlo.settings import Settings
from pymontecarlo.util.cbook import get_valid_filename
from pymontecarlo.formats.series.helper import ensure_distinc_columns
from pymontecarlo.formats.series.entrypoint import find_convert_serieshandler

# Globals and constants variables.

def create_identifiers(objs):
    settings = Settings()
    settings.set_preferred_unit('nm')
    settings.set_preferred_unit('deg')
    settings.set_preferred_unit('keV')
    settings.set_preferred_unit('g/cm^3')

    list_series = []

    for obj in objs:
        handler = find_convert_serieshandler(obj, settings)
        s = handler.convert(obj, abbreviate_name=True, format_number=True)
        list_series.append(s)

    df = pd.DataFrame(list_series)
    df = ensure_distinc_columns(df)

    identifiers = []
    for _, s in df.iterrows():
        items = ['{}={}'.format(key, value) for key, value in s.iteritems()]
        identifier = get_valid_filename('_'.join(items))
        identifiers.append(identifier)

    return identifiers

def create_identifier(obj):
    return create_identifiers([obj])[0]