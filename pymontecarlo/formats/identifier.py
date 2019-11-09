""""""

# Standard library modules.

# Third party modules.
import pandas as pd

# Local modules.
from pymontecarlo.settings import Settings
from pymontecarlo.util.cbook import get_valid_filename
from pymontecarlo.formats.dataframe import ensure_distinct_columns
from pymontecarlo.formats.series import SeriesBuilder

# Globals and constants variables.


def create_identifiers(entities):
    settings = Settings()
    settings.set_preferred_unit("nm")
    settings.set_preferred_unit("deg")
    settings.set_preferred_unit("keV")
    settings.set_preferred_unit("g/cm^3")

    list_series = []

    for entity in entities:
        builder = SeriesBuilder(settings, abbreviate_name=True, format_number=True)
        entity.convert_series(builder)

        s = builder.build()
        list_series.append(s)

    df = pd.DataFrame(list_series)
    df = ensure_distinct_columns(df)

    identifiers = []
    for _, s in df.iterrows():
        items = ["{}={}".format(key, value) for key, value in s.iteritems()]
        identifier = get_valid_filename("_".join(items))
        identifiers.append(identifier)

    return identifiers


def create_identifier(obj):
    return create_identifiers([obj])[0]
