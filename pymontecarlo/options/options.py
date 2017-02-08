"""
Main class containing all options of a simulation
"""

# Standard library modules.
import itertools

# Third party modules.

# Local modules.
from pymontecarlo.util.cbook import Builder, are_sequence_equal, unique
from pymontecarlo.options.option import Option

# Globals and constants variables.

class Options(Option):

    def __init__(self, program, beam, sample,
                 analyses=None, limits=None, models=None):
        """
        Options for a simulation.
        """
        super().__init__()

        self.program = program
        self.beam = beam
        self.sample = sample

        if analyses is None:
            analyses = []
        self.analyses = list(analyses)

        if limits is None:
            limits = []
        self.limits = list(limits)

        if models is None:
            models = []
        self.models = list(models)

    def __repr__(self):
        return '<{classname}()>' \
            .format(classname=self.__class__.__name__, **self.__dict__)

    def __eq__(self, other):
        return super().__eq__(other) and \
            self.program == other.program and \
            self.beam == other.beam and \
            self.sample == other.sample and \
            are_sequence_equal(self.analyses, other.analyses) and \
            are_sequence_equal(self.limits, other.limits) and \
            are_sequence_equal(self.models, other.models)

    def _find(self, objects, clasz):
        found_objects = []
        for obj in objects:
            if obj.__class__ == clasz:
                found_objects.append(obj)
        return found_objects

    def find_analyses(self, analysis_class):
        return self._find(self.analyses, analysis_class)

    def find_limits(self, limit_class):
        return self._find(self.limits, limit_class)

    def find_models(self, model_class):
        return self._find(self.models, model_class)

    def find_detectors(self, detector_class):
        return self._find(self.detectors, detector_class)

    @property
    def detectors(self):
        """
        Returns a :class:`tuple` of all detectors defined in the analyses.
        """
        detectors = []
        for analysis in self.analyses:
            detectors.extend(analysis.detectors)
        return tuple(unique(detectors))

    @property
    def parameters(self):
        params = super().parameters

        params.update(self.beam.parameters)
        params.update(self.sample.parameters)

        for analysis in self.analyses:
            params.update(analysis.parameters)

        for limit in self.limits:
            params.update(limit.parameters)

        for model in self.models:
            params.update(model.parameters)

        return params

class OptionsBuilder(Builder):

    def __init__(self):
        self.programs = set()
        self.beams = []
        self.samples = []
        self.analyses = []
        self.models = {}
        self.limits = {}

    def __len__(self):
        return len(self.build())

    def add_program(self, program):
        self.programs.add(program)

    def add_beam(self, beam):
        if beam not in self.beams:
            self.beams.append(beam)

    def add_sample(self, sample):
        if sample not in self.samples:
            self.samples.append(sample)

    def add_analysis(self, analysis):
        if analysis not in self.analyses:
            self.analyses.append(analysis)

    def add_limit(self, program, limit):
        self.limits.setdefault(program, []).append(limit)

    def add_model(self, program, model):
        self.models.setdefault(program, []).append(model)

    def build(self):
        list_options = []

        for program in self.programs:
            expander = program.create_expander()

            analyses = self.analyses
            analysis_combinations = expander.expand_analyses(analyses) or [(None,)]

            limits = self.limits.get(program, [])
            limit_combinations = expander.expand_limits(limits) or [(None,)]

            models = self.models.get(program, [])
            model_combinations = expander.expand_models(models) or [(None,)]

            product = itertools.product(self.beams,
                                        self.samples,
                                        analysis_combinations,
                                        limit_combinations,
                                        model_combinations)
            for beam, sample, analyses, limits, models in product:
                options = Options(program, beam, sample, analyses, limits, models)
                list_options.append(options)

                for analysis in analyses:
                    list_options.extend(analysis.apply(options))

        return list_options












