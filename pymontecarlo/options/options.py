"""
Main class containing all options of a simulation
"""

__all__ = ["Options", "OptionsBuilder"]

# Standard library modules.
import itertools

# Third party modules.
import h5py

# Local modules.
from pymontecarlo.util.cbook import unique, find_by_type, organize_by_type
from pymontecarlo.util.human import camelcase_to_words
import pymontecarlo.options.base as base

# Globals and constants variables.


class Options(base.OptionBase):
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
        return "<{classname}()>".format(
            classname=self.__class__.__name__, **self.__dict__
        )

    def __eq__(self, other):
        return (
            super().__eq__(other)
            and base.isclose(self.program, other.program)
            and base.isclose(self.beam, other.beam)
            and base.isclose(self.sample, other.sample)
            and base.are_sequence_similar(self.analyses, other.analyses)
            and base.are_sequence_similar(self.tags, other.tags)
        )

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

    # region HDF5

    ATTR_PROGRAM = "program"
    ATTR_BEAM = "beam"
    ATTR_SAMPLE = "sample"
    DATASET_ANALYSES = "analyses"
    DATASET_TAGS = "tags"

    @classmethod
    def parse_hdf5(cls, group):
        program = cls._parse_hdf5(group, cls.ATTR_PROGRAM)
        beam = cls._parse_hdf5(group, cls.ATTR_BEAM)
        sample = cls._parse_hdf5(group, cls.ATTR_SAMPLE)
        analyses = [
            cls._parse_hdf5_reference(group, reference)
            for reference in group[cls.DATASET_ANALYSES]
        ]
        tags = [str(tag) for tag in group[cls.DATASET_TAGS].asstr()]
        return cls(program, beam, sample, analyses, tags)

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(group, self.ATTR_PROGRAM, self.program)
        self._convert_hdf5(group, self.ATTR_BEAM, self.beam)
        self._convert_hdf5(group, self.ATTR_SAMPLE, self.sample)

        shape = (len(self.analyses),)
        dtype = h5py.special_dtype(ref=h5py.Reference)
        data = [
            self._convert_hdf5_reference(group, analysis) for analysis in self.analyses
        ]
        group.create_dataset(self.DATASET_ANALYSES, shape, dtype, data)

        shape = (len(self.tags),)
        dtype = h5py.special_dtype(vlen=str)
        dataset = group.create_dataset(self.DATASET_TAGS, shape, dtype)
        dataset[:] = self.tags

    # endregion

    # region Series

    def convert_series(self, builder):
        super().convert_series(builder)

        builder.add_entity(self.program)
        builder.add_entity(self.beam)
        builder.add_entity(self.sample)

        for detector in self.detectors:
            builder.add_entity(detector)

        for analysis in self.analyses:
            builder.add_entity(analysis)

        for tag in self.tags:
            builder.add_column(tag, tag, True)

    # endregion

    # region Document

    def convert_document(self, builder):
        super().convert_document(builder)

        builder.add_title("Program")
        section = builder.add_section()
        section.add_entity(self.program)

        builder.add_title("Beam")
        section = builder.add_section()
        section.add_entity(self.beam)

        builder.add_title("Sample")
        section = builder.add_section()
        section.add_entity(self.sample)

        builder.add_title("Detector" if len(self.detectors) < 2 else "Detectors")
        for clasz, detectors in organize_by_type(self.detectors).items():
            section = builder.add_section()
            section.add_title(camelcase_to_words(clasz.__name__))

            for detector in detectors:
                section.add_entity(detector)

        builder.add_title("Analysis" if len(self.analyses) < 2 else "Analyses")
        for analysis in self.analyses:
            section = builder.add_section()
            section.add_entity(analysis)

        builder.add_title("Tags")
        if self.tags:
            bullet_builder = builder.require_bullet("tags")
            for tag in self.tags:
                bullet_builder.add_item(tag)
        else:
            builder.add_text("No tags")


# endregion


class OptionsBuilder(base.OptionBuilderBase):
    def __init__(self, tags=None):
        self.programs = []
        self.beams = []
        self.samples = []
        self.analyses = []
        self.tags = list(tags) if tags is not None else []

    def __len__(self):
        count = len(self.programs) * len(self.beams) * len(self.samples)

        for program in self.programs:
            analysis_combinations = program.expander.expand_analyses(self.analyses) or [
                None
            ]
            count *= len(analysis_combinations)

        return count

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

    def iterbuild(self):
        list_options = []

        for program in self.programs:
            analyses = self.analyses
            analysis_combinations = program.expander.expand_analyses(analyses) or [None]

            product = itertools.product(self.beams, self.samples, analysis_combinations)
            for beam, sample, analyses in product:
                options = Options(program, beam, sample, analyses, self.tags)

                if options in list_options:
                    continue
                list_options.append(options)
                yield options

                for analysis in options.analyses:
                    for extra_options in analysis.apply(options):
                        if extra_options not in list_options:
                            list_options.append(extra_options)
                            yield extra_options

    def build(self):
        return list(self.iterbuild())
