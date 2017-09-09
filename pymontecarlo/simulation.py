"""
Simulation.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.util.cbook import find_by_type
from pymontecarlo.formats.series.identifier import create_identifier

# Globals and constants variables.

class Simulation(object):

    def __init__(self, options, results=None, identifier=None):
        self.options = options

        if results is None:
            results = []
        self.results = results.copy()

        if identifier is None:
            identifier = create_identifier(options)
        self.identifier = identifier

    def __eq__(self, other):
        # NOTE: This is on design since two simulations should have the
        # same or equivalent results if their options are the same
        return self.options == other.options

    def find_result(self, result_class):
        return find_by_type(self.results, result_class)
