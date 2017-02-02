"""
Main class containing all options of a simulation
"""

# Standard library modules.
import itertools

# Third party modules.

# Local modules.
from pymontecarlo.util.cbook import Builder, are_sequence_equal

# Globals and constants variables.

class Options(object):

    def __init__(self, program, beam, sample,
                 detectors=None, limits=None, models=None):
        """
        Options for a simulation.
        """
        self.program = program
        self.beam = beam
        self.sample = sample

        if detectors is None:
            detectors = []
        self.detectors = list(detectors)

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
        return self.program == other.program and \
            self.beam == other.beam and \
            self.sample == other.sample and \
            are_sequence_equal(self.detectors, other.detectors) and \
            are_sequence_equal(self.limits, other.limits) and \
            are_sequence_equal(self.models, other.models)

    def find_detectors(self, detector_class):
        pass

    def find_limits(self, limit_class):
        pass

class OptionsBuilder(Builder):

    def __init__(self):
        self.programs = set()
        self.beams = []
        self.samples = []
        self.detectors = []
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

    def add_detector(self, detector):
        if detector not in self.detectors:
            self.detectors.append(detector)

    def add_limit(self, program, limit):
        self.limits.setdefault(program, []).append(limit)

    def build(self):
        list_options = []

        for program in self.programs:
            expander = program.expander

            detectors = self.detectors
            detector_combinations = expander.expand_detectors(detectors)

            limits = self.limits.get(program, [])
            limit_combinations = expander.expand_limits(limits)

            product = itertools.product(self.beams,
                                        self.samples,
                                        detector_combinations,
                                        limit_combinations)
            for beam, sample, detectors, limits in product:
                options = Options(program, beam, sample, detectors, limits)
                list_options.append(options)

        return list_options












