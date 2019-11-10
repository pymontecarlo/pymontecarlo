""""""

# Standard library modules.
import os
import sys
import json
import itertools
import operator
import functools
import asyncio
import math

# Third party modules.
import pyxray

# Local modules.
from pymontecarlo.options.beam import GaussianBeam, CylindricalBeam, PencilBeam
from pymontecarlo.options.sample.base import SampleBase
from pymontecarlo.options.sample import (
    SubstrateSample,
    InclusionSample,
    SphereSample,
    HorizontalLayerSample,
    VerticalLayerSample,
)
from pymontecarlo.options.model import convert_models_document, ElasticCrossSectionModel
from pymontecarlo.options.analysis import PhotonIntensityAnalysis, KRatioAnalysis
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.program.base import ProgramBase, ProgramBuilderBase
from pymontecarlo.options.program.expander import (
    ExpanderBase,
    expand_to_single,
    expand_analyses_to_single_detector,
)
from pymontecarlo.options.program.exporter import ExporterBase, apply_lazy
from pymontecarlo.options.program.worker import WorkerBase
from pymontecarlo.options.program.importer import ImporterBase
from pymontecarlo.results.photonintensity import EmittedPhotonIntensityResultBuilder
from pymontecarlo.util.process import create_startupinfo

# Globals and constants variables.


class SampleMock(SampleBase):
    @property
    def materials(self):
        return []


class ExpanderMock(ExpanderBase):
    def expand_analyses(self, analyses):
        return expand_analyses_to_single_detector(analyses)

    def expand_limits(self, limits):
        return expand_to_single(limits)

    def expand_models(self, models):
        return expand_to_single(models)


class ExporterMock(ExporterBase):
    def __init__(self):
        super().__init__()

        self.beam_export_methods[GaussianBeam] = self._export_beam_gaussian
        self.beam_export_methods[CylindricalBeam] = self._export_beam_cylindrical
        self.beam_export_methods[PencilBeam] = self._export_beam_pencil

        self.sample_export_methods[SubstrateSample] = self._export_sample_substrate
        self.sample_export_methods[InclusionSample] = self._export_sample_inclusion
        self.sample_export_methods[SphereSample] = self._export_sample_sphere
        self.sample_export_methods[
            HorizontalLayerSample
        ] = self._export_sample_horizontallayers
        self.sample_export_methods[
            VerticalLayerSample
        ] = self._export_sample_verticallayers

        self.detector_export_methods[PhotonDetector] = self._export_detector_photon

        self.analysis_export_methods[
            PhotonIntensityAnalysis
        ] = self._export_analysis_photonintensity
        self.analysis_export_methods[KRatioAnalysis] = self._export_analysis_kratio

    async def _export(self, options, dirpath, erracc, dry_run=False):
        outdict = {}
        self._run_exporters(options, erracc, outdict)

        if not dry_run:
            filepath = os.path.join(dirpath, "sim.json")
            with open(filepath, "w") as fp:
                json.dump(outdict, fp)

    def _export_program(self, program, options, erracc, outdict):
        self._validate_program(program, options, erracc)

        outdict.setdefault("program", {})
        outdict["program"]["number_trajectories"] = program.number_trajectories
        outdict["program"]["elastic_cross_section_model"] = str(
            program.elastic_cross_section_model
        )

    def _validate_program(self, program, options, erracc):
        super()._validate_program(program, options, erracc)

        valid_models = [
            ElasticCrossSectionModel.RUTHERFORD,
            ElasticCrossSectionModel.MOTT_CZYZEWSKI1990,
        ]
        self._validate_model(program.elastic_cross_section_model, valid_models, erracc)

    def _validate_beam(self, beam, options, erracc):
        super()._validate_beam(beam, options, erracc)

        energy_eV = apply_lazy(beam.energy_eV, beam, options)

        if energy_eV < 5e2:
            exc = ValueError("Beam energy must be greater or equal to 500eV.")
            erracc.add_exception(exc)

    def _export_beam_cylindrical(self, beam, options, erracc, outdict):
        self._validate_beam_cylindrical(beam, options, erracc)

        outdict["beam"] = "cylindrical"

    def _export_beam_gaussian(self, beam, options, erracc, outdict):
        self._validate_beam_gaussian(beam, options, erracc)

        outdict["beam"] = "gaussian"

    def _export_beam_pencil(self, beam, options, erracc, outdict):
        self._validate_beam_pencil(beam, options, erracc)

        outdict["beam"] = "pencil"

    def _export_sample_substrate(self, sample, options, erracc, outdict):
        super()._validate_sample_substrate(sample, options, erracc)

        outdict["sample"] = "substrate"

    def _export_sample_inclusion(self, sample, options, erracc, outdict):
        super()._validate_sample_inclusion(sample, options, erracc)

        outdict["sample"] = "inclusion"

    def _export_sample_sphere(self, sample, options, erracc, outdict):
        super()._validate_sample_sphere(sample, options, erracc)

        outdict["sample"] = "sphere"

    def _export_sample_horizontallayers(self, sample, options, erracc, outdict):
        super()._validate_sample_horizontallayers(sample, options, erracc)

        outdict["sample"] = "horizontallayers"

    def _export_sample_verticallayers(self, sample, options, erracc, outdict):
        super()._validate_sample_verticallayers(sample, options, erracc)

        outdict["sample"] = "verticallayers"

    def _export_detector_photon(self, detector, options, erracc, outdict):
        super()._validate_detector_photon(detector, options, erracc)

        outdict.setdefault("detectors", []).append("photon")

    def _export_analysis_photonintensity(self, analysis, options, erracc, outdict):
        super()._validate_analysis_photonintensity(analysis, options, erracc)

        outdict.setdefault("analyses", []).append("photon intensity")

    def _export_analysis_kratio(self, analysis, options, erracc, outdict):
        super()._validate_analysis_kratio(analysis, options, erracc)

        outdict.setdefault("analyses", []).append("kratio")


class WorkerMock(WorkerBase):
    async def _run(self, token, simulation, outputdir):
        # Export
        token.update(0.1, "Exporting options")
        options = simulation.options

        await options.program.exporter.export(options, outputdir)

        # Run
        token.update(0.2, "Started")
        for i in range(10):

            args = [sys.executable, "-c", "import os; print(os.name)"]

            kwargs = {}
            kwargs["stdout"] = asyncio.subprocess.DEVNULL
            kwargs["stderr"] = asyncio.subprocess.DEVNULL
            kwargs["startupinfo"] = create_startupinfo()

            proc = await asyncio.create_subprocess_exec(*args, **kwargs)
            await proc.wait()

            await asyncio.sleep(0.01)

            token.update(0.2 + i * 6 / 100, "Running iteration {} / 10".format(i))

        # Import
        token.update(0.9, "Importing results")

        simulation.results += await options.program.importer.import_(options, outputdir)


class ImporterMock(ImporterBase):

    TRANSITIONS = (
        pyxray.xray_transition("Ka1"),
        pyxray.xray_transition("La1"),
        pyxray.xray_transition("Ma1"),
    )

    def __init__(self):
        super().__init__()

        self.import_analysis_methods[
            PhotonIntensityAnalysis
        ] = self._import_analysis_photonintensity
        self.import_analysis_methods[KRatioAnalysis] = self._import_analysis_kratio

    async def _import(self, options, dirpath, erracc):
        return self._run_importers(options, dirpath, erracc)

    def _import_analysis_photonintensity(self, options, analysis, dirpath, erracc):
        builder = EmittedPhotonIntensityResultBuilder(analysis)

        number_trajectories = options.program.number_trajectories
        beam_energy_eV = options.beam.energy_eV

        overall_composition = {}
        for material in options.sample.materials:
            for z, wf in material.composition.items():
                overall_composition.setdefault(z, 0.0)
                overall_composition[z] += wf

        total_wf = sum(overall_composition.values())

        for z, wf in overall_composition.items():
            for transition in self.TRANSITIONS:
                try:
                    energy_eV = pyxray.xray_transition_energy_eV(z, transition)
                    relative_weight = pyxray.xray_transition_relative_weight(
                        z, transition
                    )
                except pyxray.NotFound:
                    continue

                if energy_eV >= beam_energy_eV:
                    continue
                if relative_weight <= 0.01:
                    continue

                intensity = number_trajectories * (wf / total_wf) * relative_weight
                error = math.sqrt(intensity)
                builder.add_intensity((z, transition), intensity, error)

        return [builder.build()]

    def _import_analysis_kratio(self, options, analysis, dirpath, erracc):
        # Do nothing
        return []


class ProgramMock(ProgramBase):
    def __init__(
        self,
        number_trajectories=100,
        elastic_cross_section_model=ElasticCrossSectionModel.RUTHERFORD,
    ):
        super().__init__("mock")

        self._expander = ExpanderMock()
        self._exporter = ExporterMock()
        self._importer = ImporterMock()
        self._worker = WorkerMock()

        self.number_trajectories = number_trajectories
        self.elastic_cross_section_model = elastic_cross_section_model

    def __eq__(self, other):
        return (
            super().__eq__(other)
            and self.number_trajectories == other.number_trajectories
            and self.elastic_cross_section_model == other.elastic_cross_section_model
        )

    @property
    def expander(self):
        return self._expander

    @property
    def exporter(self):
        return self._exporter

    @property
    def importer(self):
        return self._importer

    @property
    def worker(self):
        return self._worker

    # region HDF5

    ATTR_NUMBER_TRAJECTORIES = "number trajectories"
    ATTR_ELASTIC_CROSS_SECTION_MODEL = "elastic cross section model"

    @classmethod
    def parse_hdf5(cls, group):
        number_trajectories = cls._parse_hdf5(group, cls.ATTR_NUMBER_TRAJECTORIES, int)
        elastic_cross_section_model = cls._parse_hdf5(
            group, cls.ATTR_ELASTIC_CROSS_SECTION_MODEL, ElasticCrossSectionModel
        )
        return cls(number_trajectories, elastic_cross_section_model)

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(
            group, self.ATTR_NUMBER_TRAJECTORIES, self.number_trajectories
        )
        self._convert_hdf5(
            group,
            self.ATTR_ELASTIC_CROSS_SECTION_MODEL,
            self.elastic_cross_section_model,
        )

    # endregion HDF5

    # region Series

    def convert_series(self, builder):
        super().convert_series(builder)
        builder.add_column("number trajectories", "ntraj", self.number_trajectories)
        builder.add_column(
            "elastic cross section model", "elastic", self.elastic_cross_section_model
        )

    # endregion

    # region Document

    def convert_document(self, builder):
        super().convert_document(builder)

        description = builder.require_description(self.DESCRIPTION_PROGRAM)
        description.add_item("Number trajectories", self.number_trajectories)

        section = builder.add_section()
        section.add_title("Models")

        convert_models_document(builder, self.elastic_cross_section_model)


# endregion


class ProgramBuilderMock(ProgramBuilderBase):
    def __init__(self):
        self.set_number_trajectories = set()
        self.elastic_cross_section_models = set()

    def __len__(self):
        it = [
            super().__len__(),
            len(self.set_number_trajectories),
            len(self.elastic_cross_section_models),
        ]
        return functools.reduce(operator.mul, it)

    def add_number_trajectories(self, number_trajectories):
        self.set_number_trajectories.add(number_trajectories)

    def add_elastic_cross_section_model(self, model):
        self.elastic_cross_section_models.add(model)

    def build(self):
        product = itertools.product(
            self.set_number_trajectories, self.elastic_cross_section_models
        )

        programs = []
        for number_trajectories, elastic_cross_section_model in product:
            program = ProgramMock(number_trajectories, elastic_cross_section_model)
            programs.append(program)

        return programs
