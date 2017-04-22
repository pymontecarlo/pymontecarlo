"""
Simulation.
"""

# Standard library modules.

# Third party modules.

# Local modules.
import pymontecarlo
from pymontecarlo.util.cbook import find_by_type, get_valid_filename
from pymontecarlo.formats.series.base import find_convert_serieshandler

# Globals and constants variables.

def create_identifier(options):
    handler = find_convert_serieshandler(options)
    s = handler.convert(options)

    try:
        preferred_units = list(pymontecarlo.settings.preferred_units.values())
        pymontecarlo.settings.clear_preferred_units(quiet=True)
        pymontecarlo.settings.set_preferred_unit('nm', quiet=True)
        pymontecarlo.settings.set_preferred_unit('deg', quiet=True)
        pymontecarlo.settings.set_preferred_unit('keV', quiet=True)
        pymontecarlo.settings.set_preferred_unit('g/cm^3', quiet=True)

        items = []
        for column, value in s.iteritems():
            key = column.abbrev
            value = column.format_value(value, tolerance=None)
            unitname = column.unitname
            items.append('{}_{}{}'.format(key, value, unitname))
    finally:
        for units in preferred_units:
            pymontecarlo.settings.set_preferred_unit(units, quiet=True)

    return get_valid_filename('_'.join(items))

class Simulation(object):

    def __init__(self, options, results=None):
        self.options = options

        if results is None:
            results = []
        self.results = results.copy()

        self.identifier = create_identifier(options)

    def __eq__(self, other):
        # NOTE: This is on design since two simulations should have the
        # same or equivalent results if their options are the same
        return self.options == other.options

    def find_result(self, result_class):
        return find_by_type(self.results, result_class)
