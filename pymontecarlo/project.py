"""
Project.
"""

# Standard library modules.
import re

# Third party modules.
import pandas as pd

# Local modules.
from pymontecarlo.util.future import FutureExecutor
from pymontecarlo.formats.hdf5.reader import HDF5ReaderMixin
from pymontecarlo.formats.hdf5.writer import HDF5WriterMixin
from pymontecarlo.formats.series.base import \
    find_convert_serieshandler, update_with_prefix
from pymontecarlo.exceptions import ConvertError

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
        if simulation in self.simulations:
            return

        identifiers = [s.identifier for s in self.simulations
                       if s.identifier.startswith(simulation.identifier)]
        if identifiers:
            last = -1
            for identifier in identifiers:
                m = re.search(r'-(\d+)$', identifier)
                if m is not None:
                    last = max(last, int(m.group(1)))

            simulation.identifier += '-{:d}'.format(last + 1)

        self.simulations.append(simulation)

    def recalculate(self):
        with RecalculateProjectExecutor() as executor:
            future = executor.submit(self)
            return future.result()

    def create_options_dataframe(self, only_different_columns=False):
        """
        Returns a :class:`pandas.DataFrame`.
        
        If *only_different_columns*, the data rows will only contain the columns
        that are different between the options.
        """
        list_series = []

        for simulation in self.simulations:
            options = simulation.options
            handler = find_convert_serieshandler(options)
            s = handler.convert(options)
            list_series.append(s)

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
        Returns a :class:`pandas.DataFrame`.
        
        If *result_classes* is a list of :class:`Result`, only the columns from
        this result classes will be returned. If ``None``, the columns from 
        all results will be returned.
        """
        list_series = []
        for simulation in self.simulations:
            s = pd.Series()

            for result in simulation.results:
                try:
                    handler = find_convert_serieshandler(result)
                except ConvertError:
                    continue

                prefix = result.getname().lower() + ' '
                s_result = handler.convert(result)

                if result_classes is None: # Include all results
                    s_result = update_with_prefix(s_result, prefix)
                    s = s.append(s_result)

                elif type(result) in result_classes:
                    if len(result_classes) == 1:
                        s = s.append(s_result)
                    else:
                        s_result = update_with_prefix(s_result, prefix)
                        s = s.append(s_result)

            list_series.append(s)

        return pd.DataFrame(list_series)

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
