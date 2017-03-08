"""
Project.
"""

# Standard library modules.

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

    def save(self, filepath=None):
        if filepath is not None:
            self.filepath = filepath

        if self.filepath is None:
            raise IOError('No file path defined')
