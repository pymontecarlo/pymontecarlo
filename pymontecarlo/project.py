"""
Project.
"""

# Standard library modules.
import re
import threading
import logging

logger = logging.getLogger(__name__)

# Third party modules.
import pandas as pd

# Local modules.
from pymontecarlo.entity import EntityBase, EntryHDF5IOMixin
from pymontecarlo.formats.dataframe import (
    create_options_dataframe,
    create_results_dataframe,
)
from pymontecarlo.util.signal import Signal

# Globals and constants variables.


class Project(EntityBase, EntryHDF5IOMixin):

    simulation_added = Signal()
    simulation_recalculated = Signal()

    def __init__(self, filepath=None):
        self.filepath = filepath
        self.simulations = []
        self.lock = threading.Lock()
        self.recalculate_required = False

    def __getstate__(self):
        with self.lock:
            return (self.filepath, self.simulations)

    def __setstate__(self, state):
        filepath, simulations = state

        self.filepath = filepath
        self.simulations = simulations
        self.recalculate_required = True

    def add_simulation(self, simulation):
        with self.lock:
            if simulation in self.simulations:
                return

            identifiers = [
                s.identifier
                for s in self.simulations
                if s.identifier.startswith(simulation.identifier)
            ]
            if identifiers:
                last = -1
                for identifier in identifiers:
                    m = re.search(r"-(\d+)$", identifier)
                    if m is not None:
                        last = max(last, int(m.group(1)))

                simulation.identifier += "-{:d}".format(last + 1)

            self.simulations.append(simulation)
            self.recalculate_required = True
            self.simulation_added.send(simulation)

    async def recalculate(self, token=None):
        with self.lock:
            if token:
                token.start()
            count = len(self.simulations)

            for i, simulation in enumerate(self.simulations):
                progress = i / count
                status = "Calculating simulation {}".format(simulation.identifier)
                if token:
                    token.update(progress, status)

                newresult = False
                for analysis in simulation.options.analyses:
                    newresult |= analysis.calculate(simulation, tuple(self.simulations))

                if newresult:
                    self.simulation_recalculated.send(simulation)

            if token:
                token.done()

            self.recalculate_required = False

    def create_options_dataframe(
        self,
        settings,
        only_different_columns=False,
        abbreviate_name=False,
        format_number=False,
    ):
        """
        Returns a :class:`pandas.DataFrame`.

        If *only_different_columns*, the data rows will only contain the columns
        that are different between the options.
        """
        list_options = [simulation.options for simulation in self.simulations]
        return create_options_dataframe(
            list_options,
            settings,
            only_different_columns,
            abbreviate_name,
            format_number,
        )

    def create_results_dataframe(
        self, settings, result_classes=None, abbreviate_name=False, format_number=False
    ):
        """
        Returns a :class:`pandas.DataFrame`.

        If *result_classes* is a list of :class:`Result`, only the columns from
        this result classes will be returned. If ``None``, the columns from
        all results will be returned.
        """
        list_results = [simulation.results for simulation in self.simulations]
        return create_results_dataframe(
            list_results, settings, result_classes, abbreviate_name, format_number
        )

    def create_dataframe(
        self,
        settings,
        only_different_columns=False,
        abbreviate_name=False,
        format_number=False,
        result_classes=None,
    ):
        """
        Returns a :class:`pandas.DataFrame`, combining the :class:`pandas.DataFrame` created
        by :meth:`.create_options_dataframe` and :meth:`.create_results_dataframe`.
        """
        df_options = self.create_options_dataframe(
            settings, only_different_columns, abbreviate_name, format_number
        )
        df_results = self.create_results_dataframe(
            settings, result_classes, abbreviate_name, format_number
        )

        return pd.concat([df_options, df_results], axis=1)

    def write(self, filepath=None):
        if filepath is None:
            filepath = self.filepath
        if filepath is None:
            raise RuntimeError("No file path given")
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

    # region HDF5

    GROUP_SIMULATIONS = "simulations"

    @classmethod
    def parse_hdf5(cls, group):
        filepath = group.file.filename
        project = cls(filepath)

        simulations = [
            cls._parse_hdf5_object(group_simulation)
            for group_simulation in group[cls.GROUP_SIMULATIONS].values()
        ]
        with project.lock:
            project.simulations.extend(simulations)

        return project

    def convert_hdf5(self, group):
        super().convert_hdf5(group)

        group_simulations = group.create_group(self.GROUP_SIMULATIONS)

        with self.lock:
            for simulation in self.simulations:
                name = simulation.identifier
                group_simulation = group_simulations.create_group(name)
                simulation.convert_hdf5(group_simulation)


# endregion
