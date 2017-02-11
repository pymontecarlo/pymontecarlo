"""
Project.
"""

# Standard library modules.
from collections import OrderedDict

# Third party modules.

# Local modules.

# Globals and constants variables.

class Project(object):

    def __init__(self, filepath=None):
        self.filepath = filepath
        self.simulations = []

    def add_simulation(self, simulation):
        if simulation not in self.simulations:
            self.simulations.append(simulation)

    def recalculate(self):
        for simulation in self.simulations:
            for analysis in simulation.options.analyses:
                analysis.calculate(simulation, tuple(self.simulations))

    def iter_datarows(self, diff=False):
        columns_options = OrderedDict()
        columns_results = OrderedDict()
        datarows_options = []
        datarows_results = []
        datarow_difference = set()

        for simulation in self.simulations:
            datarow = simulation.options.create_datarow()
            columns_options.update(datarow)
            datarows_options.append(datarow)
            datarow_difference ^= set(datarow.items())

            datarow_results = OrderedDict()
            for result in simulation.results:
                datarow = result.create_datarow()
                columns_results.update(datarow)
                datarow_results.update(datarow)
            datarows_results.append(datarow_results)

        datarow_difference = dict(datarow_difference)

        for datarow_options, datarow_results in zip(datarows_options, datarows_results):
            datarow = OrderedDict()

            for column in columns_options:
                if diff and column not in datarow_difference:
                    continue
                datarow[column] = datarow_options.get(column, None)

            for column in columns_results:
                datarow[column] = datarow_results.get(column, None)

            yield datarow

    def save(self, filepath=None):
        if filepath is not None:
            self.filepath = filepath

        if self.filepath is None:
            raise IOError('No file path defined')
