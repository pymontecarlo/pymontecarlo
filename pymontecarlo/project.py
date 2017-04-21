"""
Project.
"""

# Standard library modules.
import operator
import functools

# Third party modules.
import pandas as pd

# Local modules.
from pymontecarlo.util.future import FutureExecutor
from pymontecarlo.util.cbook import find_by_type
from pymontecarlo.formats.hdf5.reader import HDF5ReaderMixin
from pymontecarlo.formats.hdf5.writer import HDF5WriterMixin
from pymontecarlo.formats.series.options.options import OptionsSeriesHandler

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

class Project(HDF5ReaderMixin, HDF5WriterMixin):

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

    def create_options_dataframe(self, only_different_columns=False):
        """
        Returns a :class:`list` of :class:`Datarow`, one for each simulation.
        
        If *only_different_columns*, the data rows will only contain the columns
        that are different between the options.
        """
        handler = OptionsSeriesHandler()
        list_series = [handler.convert(sim.options) for sim in self.simulations]
        df = pd.DataFrame(list_series)

        if not only_different_columns or len(df) < 2:
            return df

        drop_columns = []
        for column in df.columns:
            values = df[column].values
            if all(column.compare(values[0], v) for v in values):
                drop_columns.append(column)

        df = df.drop(drop_columns, axis=1)

        return df

    def create_results_dataframe(self, result_classes=None):
        """
        Returns a :class:`list` of :class:`Datarow`, one for each simulation.
        
        If *result_classes* is a list of :class:`Result`, only the columns from
        this result classes will be returned. If ``None``, the columns from 
        all results will be returned.
        """
        if not self.simulations:
            return []

        datarows = []
        for simulation in self.simulations:
            datarow = DataRow()

            for result in find_by_type(simulation.results, DataRowCreator):
                prefix = result.getname().lower() + ' '

                if result_classes is None: # Include all results
                    datarow.update_with_prefix(prefix, result.create_datarow())

                elif type(result) in result_classes:
                    if len(result_classes) == 1:
                        datarow.update(result.create_datarow())
                    else:
                        datarow.update_with_prefix(prefix, result.create_datarow())

            datarows.append(datarow)

        return datarows

    def write(self, filepath=None):
        if filepath is not None:
            self.filepath = filepath
        super().write(filepath)

    @property
    def result_classes(self):
        """
        Returns all types of result.
        """
        classes = set()

        for simulation in self.simulations:
            classes.update(type(result) for result in simulation.results)

        return classes
