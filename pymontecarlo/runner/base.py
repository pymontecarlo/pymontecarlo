"""
Base runner.
"""

# Standard library modules.
import abc
import logging

logger = logging.getLogger(__name__)

# Third party modules.

# Local modules.
from pymontecarlo.project import Project
from pymontecarlo.simulation import Simulation
from pymontecarlo.util.cbook import unique
from pymontecarlo.formats.identifier import create_identifiers

from pymontecarlo.util.token import Token

# Globals and constants variables.


class SimulationRunnerBase(metaclass=abc.ABCMeta):
    def __init__(self, project=None, token=None, max_workers=1):
        if project is None:
            project = Project()
        self._project = project

        if token is None:
            token = Token("simulation runner")
        self._token = token

        self._submitted_options = []

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.shutdown()
        return False

    @abc.abstractmethod
    async def start(self):
        """
        Starts this runner.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def cancel(self):
        """
        Cancels all running simulations of this runner.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def shutdown(self):
        """
        Properly shutdowns this runner by waiting for all simulations to finish.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def _submit(self, simulation):
        """
        Actual implementation to submit a simulation in the queue.
        """
        raise NotImplementedError

    async def submit(self, *list_options):
        """
        Submits the options in the queue.

        If the options are not valid, a :exc:`ValidationError` is raised.

        If additional simulations are required based on the analyses of the
        submitted options, they will also be submitted.

        If a simulation with the same options already exists in the project,
        the simulation is skipped.
        """
        simulations = self.prepare_simulations(*list_options)
        logger.debug("Prepared {} simulations".format(len(simulations)))

        for simulation in simulations:
            self._submitted_options.append(simulation.options)
            await self._submit(simulation)
            logger.debug('Simulation "{}" submitted'.format(simulation.identifier))

        return simulations

    def _expand_options(self, list_options):
        final_list_options = []

        for options in list_options:
            final_list_options.append(options)

            for analysis in options.analyses:
                final_list_options.extend(analysis.apply(options))

        return unique(final_list_options)

    def _exclude_simulated_options(self, list_options):
        final_list_options = []

        for options in list_options:
            # Exclude already submitted options
            if options in self._submitted_options:
                continue

            # Exclude if simulation with same options already exists in project
            # and has results
            dummy_simulation = Simulation(options, identifier="dummy")
            if dummy_simulation in self.project.simulations:
                index = self.project.simulations.index(dummy_simulation)
                real_simulation = self.project.simulations[index]
                if real_simulation.results:
                    continue

            final_list_options.append(options)

        return final_list_options

    def _create_identifiers(self, list_options):
        if len(list_options) == 1:
            return ["simulation1"]
        return create_identifiers(list_options)

    def _create_simulations(self, list_options, identifiers):
        simulations = []

        for options, identifier in zip(list_options, identifiers):
            simulation = Simulation(options, identifier=identifier)
            simulations.append(simulation)

        return simulations

    def prepare_simulations(self, *list_options):
        """
        Performs the following operations on the provided list of options and
        returns a list of simulations.

            * Expand options to deal with additional simulations required by the
              analyses.
            * Validate all the options. Raises :exc:`ValidationError` for the
              first error found. May also create warning messages.
            * Exclude already simulated options. In other words, if an
              :class:`Options` was already submitted with this runner and
              contains results, it is excluded.
            * Exclude options already in the project of this runner.
            * Create simulations where the identifier of each simulation is
              created based on the parameters varied in the list of options.
        """
        list_options = self._expand_options(list_options)
        list_options = self._exclude_simulated_options(list_options)

        identifiers = self._create_identifiers(list_options)

        simulations = self._create_simulations(list_options, identifiers)

        return simulations

    async def set_project(self, project):
        """
        If the runner is running, all the tasks will be cancelled.
        """
        await self.cancel()
        self._project = project
        self._submitted_options.clear()
        self._token.reset()

    @property
    def project(self):
        """
        Either project giving to this runner or project created by this runner.
        """
        return self._project

    @property
    def token(self):
        """
        Token of this runner to track state, progress and status of simulations.
        """
        return self._token
