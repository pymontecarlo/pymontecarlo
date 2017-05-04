"""
Main class containing all options of a simulation
"""

# Standard library modules.
import itertools

# Third party modules.

# Local modules.
from pymontecarlo.util.cbook import are_sequence_similar, unique, find_by_type
from pymontecarlo.options.base import Option, OptionBuilder

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
        # NOTE: Here we only care that two programs have the same identifier
        return super().__eq__(other) and \
            self.program.getidentifier() == other.program.getidentifier() and \
            self.beam == other.beam and \
            self.sample == other.sample and \
            are_sequence_similar(self.analyses, other.analyses) and \
            are_sequence_similar(self.limits, other.limits) and \
            are_sequence_similar(self.models, other.models)

    def find_analyses(self, analysis_class):
        return find_by_type(self.analyses, analysis_class)

    def find_limits(self, limit_class):
        return find_by_type(self.limits, limit_class)

    def find_models(self, model_class):
        return find_by_type(self.models, model_class)

    def find_detectors(self, detector_class):
        return find_by_type(self.detectors, detector_class)

    @property
    def detectors(self):
        """
        Returns a :class:`tuple` of all detectors defined in the analyses.
        """
        detectors = []
        for analysis in self.analyses:
            detectors.extend(analysis.detectors)
        return tuple(unique(detectors))

class OptionsBuilder(OptionBuilder):

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
        self.limits.setdefault(program, [])
        if limit not in self.limits[program]:
            self.limits[program].append(limit)

    def add_model(self, program, model):
        self.models.setdefault(program, [])
        if model not in self.models[program]:
            self.models[program].append(model)

    def build(self):
        list_options = []

        for program in self.programs:
            expander = program.create_expander()

            analyses = self.analyses
            analysis_combinations = expander.expand_analyses(analyses) or [None]

            limits = self.limits.get(program, [])
            limit_combinations = expander.expand_limits(limits) or [None]

            models = self.models.get(program, [])
            model_combinations = expander.expand_models(models) or [None]

            product = itertools.product(self.beams,
                                        self.samples,
                                        analysis_combinations,
                                        limit_combinations,
                                        model_combinations)
            for beam, sample, analyses, limits, models in product:
                options = Options(program, beam, sample, analyses, limits, models)

                if options in list_options:
                    continue
                list_options.append(options)

                for analysis in options.analyses:
                    for extra_options in analysis.apply(options):
                        if extra_options not in list_options:
                            list_options.append(extra_options)

        return list_options












