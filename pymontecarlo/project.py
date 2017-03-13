"""
Project.
"""

# Standard library modules.
import threading

# Third party modules.

# Local modules.
from pymontecarlo.util.future import FutureExecutor

# Globals and constants variables.

class RecalculateProjectExecutor(FutureExecutor):

    def submit(self, project):
        def target(token, project):
            simulations = list(project.simulations)
            count = len(simulations)

            for i, simulation in enumerate(simulations):
                if token.cancelled():
                    break

                progress = i / count
                status = 'Calculating simulation {}'.format(simulation.identifier)
                token.update(progress, status)

                for analysis in simulation.options.analyses:
                    analysis.calculate(simulation, tuple(simulations))

        return self._submit(target, project)

class Project(object):

    def __init__(self, filepath=None):
        self.filepath = filepath
        self.simulations = []
        self.lock = threading.Lock()

    def add_simulation(self, simulation):
        if simulation not in self.simulations:
            self.simulations.append(simulation)

    def recalculate(self):
        with RecalculateProjectExecutor() as executor:
            future = executor.submit(self)
            return future.result()

    def save(self, filepath=None):
        if filepath is not None:
            self.filepath = filepath

        if self.filepath is None:
            raise IOError('No file path defined')
