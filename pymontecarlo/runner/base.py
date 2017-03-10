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

    def _prepare_simulation(self, options):
        program = options.program
        validator = program.create_validator()
        options = validator.validate_options(options)
        return Simulation(options)

    @abc.abstractmethod
    def _prepare_target(self):
        raise NotImplementedError

    def submit(self, options):
        """
        Submits the options in the queue and returns a :class:`Future` object.
        """
        simulation = self._prepare_simulation(options)
        target = self._prepare_target()
        return super().submit(target, simulation)

