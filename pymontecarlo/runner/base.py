"""
Base runner.
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.project import Project
from pymontecarlo.simulation import Simulation
from pymontecarlo.util.future import FutureExecutor, Token, FutureAdapter
from pymontecarlo.util.cbook import unique
from pymontecarlo.formats.series.base import create_identifier
from pymontecarlo.formats.series.options.base import create_options_dataframe

# Globals and constants variables.

class SimulationRunner(FutureExecutor, metaclass=abc.ABCMeta):

    def __init__(self, project=None, max_workers=1):
        super().__init__(max_workers)
        self.submitted_options = []

        if project is None:
            project = Project()
        self.project = project

    def _on_done(self, future):
        simulation = super()._on_done(future)

        if simulation:
            self.project.add_simulation(simulation)

        else:
            try:
                options = future.args[0].options
                self.submitted_options.remove(options)
            except:
                pass

        # Recalculate if all other futures are done and recalculation is required
        if not self.executor._shutdown and self.done() and self.project.recalculate_required:
            target = self.project.recalculate
            token = Token()
            future = self.executor.submit(target, token)

            future2 = FutureAdapter(future, token, (), {})
            self.futures.add(future2)
            self.submitted.send(future2)

    def _expand_options(self, list_options):
        final_list_options = []

        for options in list_options:
            final_list_options.append(options)

            for analysis in options.analyses:
                final_list_options.extend(analysis.apply(options))

        return unique(final_list_options)

    def _validate_options(self, list_options):
        valid_list_options = []

        for options in list_options:
            program = options.program
            validator = program.create_validator()
            valid_options = validator.validate_options(options)
            valid_list_options.append(valid_options)

        return valid_list_options

    def _exclude_simulated_options(self, list_options):
        final_list_options = []

        for options in list_options:
            # Exclude already submitted options
            if options in self.submitted_options:
                continue

            # Exclude if simulation with same options already exists in project
            # and has results
            dummy_simulation = Simulation(options, identifier='dummy')
            if dummy_simulation in self.project.simulations:
                index = self.project.simulations.index(dummy_simulation)
                real_simulation = self.project.simulations[index]
                if real_simulation.results:
                    continue

            final_list_options.append(options)

        return final_list_options

    def _create_identifiers(self, list_options):
        df = create_options_dataframe(list_options, only_different_columns=True)

        identifiers = []
        for _index, series in df.iterrows():
            identifiers.append(create_identifier(series))

        return identifiers

    def _create_simulations(self, list_options, identifiers):
        simulations = []

        for options, identifier in zip(list_options, identifiers):
            simulation = Simulation(options, identifier=identifier)
            simulations.append(simulation)

        return simulations

    def _prepare_simulations(self, list_options):
        list_options = self._expand_options(list_options)
        list_options = self._validate_options(list_options)
        list_options = self._exclude_simulated_options(list_options)

        identifiers = self._create_identifiers(list_options)

        simulations = self._create_simulations(list_options, identifiers)

        return simulations

    @abc.abstractmethod
    def _prepare_target(self):
        raise NotImplementedError

    def submit(self, *list_options):
        """
        Submits the options in the queue.
        
        If the options are not valid, a :exc:`ValidationError` is raised.
        
        If additional simulations are required based on the analyses of the
        submitted options, they will also be submitted.
        
        If a simulation with the same options already exists in the project,
        the simulation is skipped.
        
        :return: a list of :class:`Future` object, one for each launched 
            simulation
        """
        simulations = self._prepare_simulations(list_options)
        target = self._prepare_target()

        futures = []
        for simulation in simulations:
            self.submitted_options.append(simulation.options)
            future = self._submit(target, simulation)
            futures.append(future)

        return futures

    def shutdown(self):
        super().shutdown()
        self.submitted_options.clear()
