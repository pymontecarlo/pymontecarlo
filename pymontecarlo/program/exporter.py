"""
Base class for exporters
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.exceptions import ExportError

# Globals and constants variables.

class Exporter(object, metaclass=abc.ABCMeta):
    """
    Base class for all exporters.
    """

    def __init__(self):
        self.beam_export_methods = {}
        self.sample_export_methods = {}
        self.detector_export_methods = {}
        self.analysis_export_methods = {}
        self.limit_export_methods = {}
        self.model_export_methods = {}

    def export(self, options, dirpath):
        """
        Exports options to the specified output directory.
        It is assumed that the options object is valid for this program.

        :arg options: options to export
        :arg dirpath: full path to output directory
        """
        errors = set()
        self._export(options, dirpath, errors)

        if errors:
            raise ExportError(*errors)

    @abc.abstractmethod
    def _export(self, options, dirpath, errors):
        """
        Performs the actual export.
        
        :arg options: options to export
        :arg dirpath: full path to output directory
        :arg errors: :class:`set` to accumulate encountered errors
        """
        raise NotImplementedError

    def _run_exporters(self, options, errors, *args, **kwargs):
        """
        Internal command to call the register export functions. 
        All optional arguments passed to this method are transferred to the
        export methods.
        """
        self._export_beam(options.beam, options, errors, *args, **kwargs)
        self._export_sample(options.sample, options, errors, *args, **kwargs)
        self._export_detectors(options.detectors, options, errors, *args, **kwargs)
        self._export_analyses(options.analyses, options, errors, *args, **kwargs)
        self._export_limits(options.limits, options, errors, *args, **kwargs)
        self._export_models(options.models, options, errors, *args, **kwargs)

    def _export_beam(self, beam, options, errors, *args, **kwargs):
        beam_class = beam.__class__
        if beam_class not in self.beam_export_methods:
            exc = ValueError('Beam ({0}) is not supported.'
                             .format(beam_class.__name__))
            errors.add(exc)
            return

        method = self.beam_export_methods[beam_class]
        method(beam, options, errors, *args, **kwargs)

    def _export_sample(self, sample, options, errors, *args, **kwargs):
        sample_class = sample.__class__
        if sample_class not in self.sample_export_methods:
            exc = ValueError('Sample ({0}) is not supported.'
                             .format(sample_class.__name__))
            errors.add(exc)
            return

        method = self.sample_export_methods[sample_class]
        method(sample, options, errors, *args, **kwargs)

    def _export_detectors(self, detectors, options, errors, *args, **kwargs):
        for detector in detectors:
            self._export_detector(detector, options, errors, *args, **kwargs)

    def _export_detector(self, detector, options, errors, *args, **kwargs):
        detector_class = detector.__class__
        if detector_class not in self.detector_export_methods:
            exc = ValueError('Detector ({0}) is not supported.'
                             .format(detector_class.__name__))
            errors.add(exc)
            return

        method = self.detector_export_methods[detector_class]
        method(detector, options, errors, *args, **kwargs)

    def _export_analyses(self, analyses, options, errors, *args, **kwargs):
        for analysis in analyses:
            self._export_analysis(analysis, options, errors, *args, **kwargs)

    def _export_analysis(self, analysis, options, errors, *args, **kwargs):
        analysis_class = analysis.__class__
        if analysis_class not in self.analysis_export_methods:
            exc = ValueError('Analysis ({0}) is not supported.'
                             .format(analysis_class.__name__))
            errors.add(exc)
            return

        method = self.analysis_export_methods[analysis_class]
        method(analysis, options, errors, *args, **kwargs)

    def _export_limits(self, limits, options, errors, *args, **kwargs):
        for limit in limits:
            self._export_limit(limit, options, errors, *args, **kwargs)

    def _export_limit(self, limit, options, errors, *args, **kwargs):
        limit_class = limit.__class__
        if limit_class not in self.limit_export_methods:
            exc = ValueError('Limit ({0}) is not supported.'
                             .format(limit_class.__name__))
            errors.add(exc)
            return

        method = self.limit_export_methods[limit_class]
        method(limit, options, errors, *args, **kwargs)

    def _export_models(self, models, options, errors, *args, **kwargs):
        for model in models:
            self._export_model(model, options, errors, *args, **kwargs)

    def _export_model(self, model, options, errors, *args, **kwargs):
        model_class = model.__class__
        if model_class not in self.model_export_methods:
            exc = ValueError('Model ({0}) is not supported.'
                             .format(model_class.__name__))
            errors.add(exc)
            return

        method = self.model_export_methods[model_class]
        method(model, options, errors, *args, **kwargs)

