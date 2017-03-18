"""
Project.
"""

# Standard library modules.
import operator
import functools

# Third party modules.

# Local modules.
from pymontecarlo.util.future import FutureExecutor
from pymontecarlo.util.cbook import find_by_type
from pymontecarlo.util.datarow import DataRowCreator

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

    def add_simulation(self, simulation):
        if simulation not in self.simulations:
            self.simulations.append(simulation)

    def recalculate(self):
        with RecalculateProjectExecutor() as executor:
            future = executor.submit(self)
            return future.result()

    def create_datarows(self, only_different_options=False, result_classes=None):
        """
        Returns a :class:`list` of :class:`Datarow`, one for each simulation.
        
        If *only_different_options*, the data rows will only contain the columns
        that are different between the options.
        
        If *result_classes* is a list of :class:`Result`, only the columns from
        this result classes will be returned. If ``None``, the data row will
        only contain the columns from the options.
        """
        if not self.simulations:
            return []

        if result_classes is None:
            result_classes = []

        # Options
        datarows = []
        for simulation in self.simulations:
            datarow = simulation.options.create_datarow()
            datarows.append(datarow)

        if only_different_options:
            tmpdatarows = []

            for datarow in datarows:
                newdatarow = functools.reduce(operator.or_, [datarow ^ other for other in datarows])
                tmpdatarows.append(newdatarow)

            datarows = tmpdatarows

        # Results
        for simulation, datarow in zip(self.simulations, datarows):
            for result in find_by_type(simulation.results, DataRowCreator):
                if type(result) not in result_classes:
                    continue
                prefix = result.getname().lower() + ' '
                datarow.update_with_prefix(prefix, result.create_datarow())

        return datarows

    def save(self, filepath=None):
        if filepath is not None:
            self.filepath = filepath

        if self.filepath is None:
            raise IOError('No file path defined')
