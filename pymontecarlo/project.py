"""
Project.
"""

# Standard library modules.
import re
import threading

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.reader import HDF5ReaderMixin
from pymontecarlo.formats.hdf5.writer import HDF5WriterMixin
from pymontecarlo.formats.series.options.base import create_options_dataframe
from pymontecarlo.formats.series.results.base import create_results_dataframe
from pymontecarlo.util.signal import Signal

# Globals and constants variables.

class Project(HDF5ReaderMixin, HDF5WriterMixin):

    simulation_added = Signal()
    recalculated = Signal()

    def __init__(self, filepath=None):
        self.filepath = filepath
        self.simulations = []
        self.lock = threading.Lock()
        self.recalculate_required = False

    def add_simulation(self, simulation):
        with self.lock:
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
            self.recalculate_required = True
            self.simulation_added.send(simulation)

    def recalculate(self, token=None):
        with self.lock:
            count = len(self.simulations)

            for i, simulation in enumerate(self.simulations):
                if token and token.cancelled():
                    break

                progress = i / count
                status = 'Calculating simulation {}'.format(simulation.identifier)
                if token: token.update(progress, status)

                for analysis in simulation.options.analyses:
                    analysis.calculate(simulation, tuple(self.simulations))

            if token: token.update(1.0, 'Done')

            self.recalculate_required = False
            self.recalculated.send()

    def create_options_dataframe(self, only_different_columns=False):
        """
        Returns a :class:`pandas.DataFrame`.
        
        If *only_different_columns*, the data rows will only contain the columns
        that are different between the options.
        """
        list_options = [simulation.options for simulation in self.simulations]
        return create_options_dataframe(list_options, only_different_columns)

    def create_results_dataframe(self, result_classes=None):
        """
        Returns a :class:`pandas.DataFrame`.
        
        If *result_classes* is a list of :class:`Result`, only the columns from
        this result classes will be returned. If ``None``, the columns from 
        all results will be returned.
        """
        list_results = [simulation.results for simulation in self.simulations]
        return create_results_dataframe(list_results, result_classes)

    def write(self, filepath=None):
        if filepath is None:
            filepath = self.filepath
        if filepath is None:
            raise RuntimeError('No file path given')
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
