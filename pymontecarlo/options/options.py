"""
Main class containing all options of a simulation
"""

__all__ = ['Options', 'OptionsBuilder']

# Standard library modules.
import itertools

# Third party modules.

# Local modules.
from pymontecarlo.util.cbook import are_sequence_similar, unique, find_by_type
from pymontecarlo.options.base import OptionBase, OptionBuilderBase

# Globals and constants variables.

class Options(OptionBase):

    def __init__(self, program, beam, sample, analyses=None, tags=None):
        """
        Options for a simulation.
        """
        super().__init__()

        self.program = program
        self.beam = beam
        self.sample = sample
        self.analyses = list(analyses) if analyses is not None else []
        self.tags = list(tags) if tags is not None else []

    def __repr__(self):
        return '<{classname}()>' \
            .format(classname=self.__class__.__name__, **self.__dict__)

    def __eq__(self, other):
        return super().__eq__(other) and \
            self.program == other.program and \
            self.beam == other.beam and \
            self.sample == other.sample and \
            are_sequence_similar(self.analyses, other.analyses) and \
            are_sequence_similar(self.tags, other.tags)

    def find_analyses(self, analysis_class, detector=None):
        """
        Finds all analyses matching the specified class.
        If *detector* is not ``None``, the analysis detector must also be
        equal to the specified detector.
        
        :return: :class:`list` of analysis objects
        """
        analyses = find_by_type(self.analyses, analysis_class)

        if detector is None:
            return analyses

        return [analysis for analysis in analyses if analysis.detector == detector]

    def find_detectors(self, detector_class):
        return find_by_type(self.detectors, detector_class)

    @property
    def detectors(self):
        """
        Returns a :class:`tuple` of all detectors defined in the analyses.
        """
        return tuple(unique(analysis.detector for analysis in self.analyses))

class OptionsBuilder(OptionBuilderBase):

    def __init__(self, tags=None):
        self.programs = []
        self.beams = []
        self.samples = []
        self.analyses = []
        self.tags = list(tags) if tags is not None else []

    def __len__(self):
        return len(self.build())

    def add_program(self, program):
        if program not in self.programs:
            self.programs.append(program)

    def add_beam(self, beam):
        if beam not in self.beams:
            self.beams.append(beam)

    def add_sample(self, sample):
        if sample not in self.samples:
            self.samples.append(sample)

    def add_analysis(self, analysis):
        if analysis not in self.analyses:
            self.analyses.append(analysis)

    def build(self):
        list_options = []

        for program in self.programs:
            analyses = self.analyses
            analysis_combinations = program.expander.expand_analyses(analyses) or [None]

            product = itertools.product(self.beams,
                                        self.samples,
                                        analysis_combinations)
            for beam, sample, analyses in product:
                options = Options(program, beam, sample, analyses, self.tags)

                if options in list_options:
                    continue
                list_options.append(options)

                for analysis in options.analyses:
                    for extra_options in analysis.apply(options):
                        if extra_options not in list_options:
                            list_options.append(extra_options)

        return list_options












