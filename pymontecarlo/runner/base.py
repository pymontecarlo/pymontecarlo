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

    def _prepare_simulations(self, options, simulations=None):
        if simulations is None:
            simulations = []

        for analysis in options.analyses:
            for other_options in analysis.apply(options):
                self._prepare_simulations(other_options, simulations)

        # Validate
        program = options.program
        validator = program.create_validator()
        options = validator.validate_options(options)

        # Create simulation
        simulation = Simulation(options)

        # Check if it has been submitted
        if options in self.submitted_options:
            return simulations

        if simulation in self.project.simulations:
            return simulations

        # Add to submission list
        self.submitted_options.append(options)
        simulations.append(simulation)

        return simulations

    @abc.abstractmethod
    def _prepare_target(self):
        raise NotImplementedError

    def submit(self, options):
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
        simulations = self._prepare_simulations(options)
        target = self._prepare_target()

        futures = []
        for simulation in simulations:
            future = self._submit(target, simulation)
            futures.append(future)

        return futures

    def shutdown(self):
        super().shutdown()
        self.submitted_options.clear()
