"""
Main class containing all options of a simulation
"""

# Standard library modules.
import uuid
import itertools

# Third party modules.

# Local modules.
from pymontecarlo.util.cbook import Builder
from pymontecarlo.exceptions import ValidationError

# Globals and constants variables.

class Options(object):

    def __init__(self, program, beam, sample,
                 detectors=None, limits=None, models=None):
        """
        Options for a simulation.
        """
        self.uuid = uuid.uuid4().hex
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
        return '<{classname}({uuid})>' \
            .format(classname=self.__class__.__name__, **self.__dict__)

class OptionsBuilder(Builder):

    MODE_IGNORE = 'ignore' # Remove incompatible or invalid options
    MODE_STRICT = 'strict' # Raise exceptions for incompatible and invalid options

    def __init__(self, mode=MODE_IGNORE):
        self.mode = mode
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

    def add_limit(self, program, limit):
        self.limits.setdefault(program, []).append(limit)

    def build(self):
        list_options = []

        for program in self.programs:
            expander = program.expander
            converter = program.converter
            validator = program.validator

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

                options = converter.convert_options(options)

                try:
                    validator.validate_options(options)
                except ValidationError:
                    if self.mode == self.MODE_STRICT:
                        raise
                else:
                    list_options.append(options)

        return list_options












