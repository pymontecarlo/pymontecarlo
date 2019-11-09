"""
Base importer.
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.exceptions import ImportError, ImportWarning
from pymontecarlo.util.error import ErrorAccumulator

# Globals and constants variables.


class ImporterBase(metaclass=abc.ABCMeta):
    def __init__(self):
        self.import_analysis_methods = {}

    async def import_(self, options, dirpath):
        """
        Imports the results and returns a :class:`list` of :class:`Result`.

        :arg options: options used for the simulation
        :arg dirpath: path containing the simulation files
        """
        with ErrorAccumulator(ImportWarning, ImportError) as erracc:
            return await self._import(options, dirpath, erracc)

    @abc.abstractmethod
    async def _import(self, options, dirpath, erracc):
        """
        Performs the actual import.
        """
        raise NotImplementedError

    def _run_importers(self, options, dirpath, erracc, *args, **kwargs):
        """
        Internal command to call the register import functions. 
        All optional arguments passed to this method are transferred to the
        import methods.
        """
        return self._import_analyses(options, dirpath, erracc, *args, **kwargs)

    def _import_analyses(self, options, dirpath, erracc, *args, **kwargs):
        results = []

        for analysis in options.analyses:
            results += self._import_analysis(
                options, analysis, dirpath, erracc, *args, **kwargs
            )

        return results

    def _import_analysis(self, options, analysis, dirpath, erracc, *args, **kwargs):
        analysis_class = analysis.__class__
        if analysis_class not in self.import_analysis_methods:
            exc = ValueError(
                "Analysis ({0}) is not supported.".format(analysis_class.__name__)
            )
            erracc.add_exception(exc)
            return

        method = self.import_analysis_methods[analysis_class]
        return method(options, analysis, dirpath, erracc, *args, **kwargs)
