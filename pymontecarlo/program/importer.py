"""
Base importer.
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.exceptions import ImportError_
from pymontecarlo.simulation import Simulation

# Globals and constants variables.

class Importer(metaclass=abc.ABCMeta):

    def __init__(self):
        self.import_analysis_methods = {}

    def import_(self, options, dirpath):
        """
        Imports the results and returns a :class:`Simulation`

        :arg options: options used for the simulation
        :arg dirpath: path containing the simulation files
        """
        errors = set()
        simulation = self._import(options, dirpath, errors)

        if errors:
            raise ImportError_(*errors)

        return simulation

    @abc.abstractmethod
    def _import(self, options, dirpath, errors):
        """
        Performs the actual import.
        """
        raise NotImplementedError

    def _create_simulation(self, options):
        """
        Creates the simulation object.
        """
        return Simulation(options)

    def _run_importers(self, simulation, dirpath, errors, *args, **kwargs):
        """
        Internal command to call the register import functions. 
        All optional arguments passed to this method are transferred to the
        import methods.
        """
        analyses = simulation.options.analyses
        self._import_analyses(analyses, simulation, dirpath, errors, *args, **kwargs)

    def _import_analyses(self, analyses, simulation, dirpath, errors, *args, **kwargs):
        for analysis in analyses:
            self._import_analysis(analysis, simulation, dirpath, errors, *args, **kwargs)

    def _import_analysis(self, analysis, simulation, dirpath, errors, *args, **kwargs):
        analysis_class = analysis.__class__
        if analysis_class not in self.import_analysis_methods:
            exc = ValueError('Analysis ({0}) is not supported.'
                             .format(analysis_class.__name__))
            errors.add(exc)
            return

        method = self.import_analysis_methods[analysis_class]
        method(analysis, simulation, dirpath, errors, *args, **kwargs)
