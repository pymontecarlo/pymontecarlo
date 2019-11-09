#!/usr/bin/env python
"""
Base worker
"""

# Standard library modules.
import abc
import asyncio

# Third party modules.

# Local modules.

# Globals and constants variables.


class WorkerBase(metaclass=abc.ABCMeta):
    """
    Base class for all workers.
    A worker is used to run one simulation with a given program and
    return their results.

    A worker should not be directly used to start a simulation.
    One should rather use a runner.
    """

    async def run(self, token, simulation, outputdir):
        """
        Creates and runs a simulation from the specified options.
        
        The worker is responsible to:
        
            * export the simulation options to the file format of the Monte Carlo program
            * run the simulation
            * import the simulation results and place them in the simulation

        Args:
            token (:class:`Token`): token to track the progress of this simulation.
            simulation (:class:`Simulation`): simulation containing options to simulate
            outputdir (str): directory where to save simulation results.
            
        Returns:
            :class:`Simulation`: simulation
            
        Raises:
            ExportError: if the export fails
            WorkerError: if the worker fails
            ImportError: if the import fails
        """
        token.start()

        try:
            await self._run(token, simulation, outputdir)
        except asyncio.CancelledError:
            token.cancel()
            raise
        except Exception as exc:
            token.error(str(exc))
            raise

        token.done()

        return simulation

    @abc.abstractmethod
    async def _run(self, token, simulation, outputdir):
        """
        Actual implementation to run a simulation. 
        The :meth:`run` takes care of handling the cancellation and 
        error exceptions with the token.
        
        Args:
            token (:class:`Token`): token to track the progress of this simulation.
            simulation (:class:`Simulation`): simulation containing options to simulate
            outputdir (str): directory where to save simulation results.
        """
        raise NotImplementedError
