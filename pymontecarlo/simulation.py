"""
Simulation.
"""

# Standard library modules.
import uuid

# Third party modules.

# Local modules.
from pymontecarlo.util.cbook import find_by_type

# Globals and constants variables.

class Simulation(object):

    def __init__(self, options, results=None):
        self._identifier = str(uuid.uuid4())
        self.options = options

        if results is None:
            results = []
        self.results = results.copy()

    def find_result(self, result_class):
        return find_by_type(self.results, result_class)

    @property
    def identifier(self):
        return self._identifier
