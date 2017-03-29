"""
Base runner.
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.project import Project
from pymontecarlo.simulation import Simulation
from pymontecarlo.util.future import FutureExecutor

# Globals and constants variables.

class SimulationRunner(FutureExecutor, metaclass=abc.ABCMeta):

    def __init__(self, project=None, max_workers=1):
        super().__init__(max_workers)

        if project is None:
            project = Project()
        self.project = project

    def _on_done(self, future):
        simulation = super()._on_done(future)
        if simulation:
            self.project.add_simulation(simulation)

    def _prepare_simulations(self, options, simulations=None):
        if simulations is None:
            simulations = []

        for analysis in options.analyses:
            for other_options in analysis.apply(options):
                self._prepare_simulations(other_options, simulations)

        program = options.program
        validator = program.create_validator()
        options = validator.validate_options(options)
        simulation = Simulation(options)
        if simulation not in self.project.simulations:
            simulations.append(simulation)

        return simulations

    @abc.abstractmethod
    def _prepare_target(self):
        raise NotImplementedError

    def submit(self, options):
        """
        Submits the options in the queue.
        If a simulation with the same options already exists in the project,
        the simulation is skipped.
        If additional simulations are required based on the analyses of the
        submitted options, they will also be submitted.
        
        :return: a list of :class:`Future` object, one for each launched 
            simulation
        """
        simulations = self._prepare_simulations(options)
        target = self._prepare_target()

        futures = []
        for simulation in simulations:
            future = self._submit(target, simulation)
            futures.append(future)

        return futures
