#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.mock import ExporterMock, ProgramMock
from pymontecarlo.options import Material, VACUUM
from pymontecarlo.options.beam import GaussianBeam, CylindricalBeam
from pymontecarlo.options.sample import (
    SubstrateSample,
    InclusionSample,
    SphereSample,
    HorizontalLayerSample,
    VerticalLayerSample,
)
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.analysis import PhotonIntensityAnalysis, KRatioAnalysis
from pymontecarlo.options.model import (
    ElasticCrossSectionModel,
    MassAbsorptionCoefficientModel,
)
from pymontecarlo.util.error import ErrorAccumulator

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)


@pytest.fixture
def exporter():
    return ExporterMock()


@pytest.mark.asyncio
async def test_export(event_loop, exporter, options, tmp_path):
    await exporter.export(options, tmp_path)

    assert tmp_path.joinpath("sim.json").exists()


@pytest.mark.asyncio
async def test_export_dry_run(event_loop, exporter, options, tmp_path):
    await exporter.export(options, tmp_path, dry_run=True)

    assert not tmp_path.joinpath("sim.json").exists()


def test_validate_material_invalid(exporter, options):
    material = Material(" ", {120: 1.1}, -1.0, "blah")

    erracc = ErrorAccumulator()
    exporter._validate_material(material, options, erracc)

    assert len(erracc.exceptions) == 6
    assert len(erracc.warnings) == 0


def test_validate_material_nodensity(exporter, options):
    material = Material("Pure Cu", {29: 1.0})

    erracc = ErrorAccumulator()
    exporter._validate_material(material, options, erracc)

    assert material.density_kg_per_m3 is not None
    assert len(erracc.exceptions) == 0
    assert len(erracc.warnings) == 0


def test_validate_program_invalid(exporter, options):
    program = ProgramMock("bar", ElasticCrossSectionModel.ELSEPA2005)

    erracc = ErrorAccumulator()
    exporter._validate_program(program, options, erracc)

    assert len(erracc.exceptions) == 1
    assert len(erracc.warnings) == 0


def test_validate_program_invalid2(exporter, options):
    program = ProgramMock("bar", MassAbsorptionCoefficientModel.POUCHOU_PICHOIR1991)

    erracc = ErrorAccumulator()
    exporter._validate_program(program, options, erracc)

    assert len(erracc.exceptions) == 1
    assert len(erracc.warnings) == 0


def test_validate_beam_cylindrical_invalid(exporter, options):
    beam = CylindricalBeam(0.0, -1.0, "particle", float("inf"), float("nan"))

    erracc = ErrorAccumulator()
    exporter._validate_beam_cylindrical(beam, options, erracc)

    assert len(erracc.exceptions) == 6
    assert len(erracc.warnings) == 0


def test_validate_beam_gaussian_invalid(exporter, options):
    beam = GaussianBeam(0.0, -1.0, "particle", float("inf"), float("nan"))

    erracc = ErrorAccumulator()
    exporter._validate_beam_gaussian(beam, options, erracc)

    assert len(erracc.exceptions) == 6
    assert len(erracc.warnings) == 0


def test_validate_sample_substrate_invalid(exporter, options):
    sample = SubstrateSample(VACUUM, float("inf"), float("nan"))

    erracc = ErrorAccumulator()
    exporter._validate_sample_substrate(sample, options, erracc)

    assert len(erracc.exceptions) == 3
    assert len(erracc.warnings) == 0


def test_validate_sample_inclusion_invalid(exporter, options):
    sample = InclusionSample(VACUUM, VACUUM, 0.0)

    erracc = ErrorAccumulator()
    exporter._validate_sample_inclusion(sample, options, erracc)

    assert len(erracc.exceptions) == 3
    assert len(erracc.warnings) == 0


def test_validate_sample_sphere_invalid(exporter, options):
    sample = SphereSample(VACUUM, -1.0)

    erracc = ErrorAccumulator()
    exporter._validate_sample_sphere(sample, options, erracc)

    assert len(erracc.exceptions) == 2
    assert len(erracc.warnings) == 0


def test_validate_sample_horizontallayers_invalid(exporter, options):
    sample = HorizontalLayerSample(COPPER)
    sample.add_layer(ZINC, -1.0)

    erracc = ErrorAccumulator()
    exporter._validate_sample_horizontallayers(sample, options, erracc)

    assert len(erracc.exceptions) == 1
    assert len(erracc.warnings) == 0


def test_validate_sample_verticallayers_invalid(exporter, options):
    sample = VerticalLayerSample(VACUUM, VACUUM)
    sample.add_layer(ZINC, -1.0)

    erracc = ErrorAccumulator()
    exporter._validate_sample_verticallayers(sample, options, erracc)

    assert len(erracc.exceptions) == 3
    assert len(erracc.warnings) == 0


def test_validate_detector_photon_invalid(exporter, options):
    detector = PhotonDetector("", 2.0, -1.0)

    erracc = ErrorAccumulator()
    exporter._validate_detector_photon(detector, options, erracc)

    assert len(erracc.exceptions) == 3
    assert len(erracc.warnings) == 0


def test_validate_analysis_photonintensity(exporter, options):
    detector = PhotonDetector("test", 1.0, 1.0)
    analysis = PhotonIntensityAnalysis(detector)

    erracc = ErrorAccumulator()
    exporter._validate_analysis_photonintensity(analysis, options, erracc)

    assert len(erracc.exceptions) == 0
    assert len(erracc.warnings) == 0


def test_validate_analysis_kratio_invalid(exporter, options):
    detector = PhotonDetector("test", 1.0, 1.0)
    analysis = KRatioAnalysis(detector)
    analysis.add_standard_material(14, Material.pure(13))

    erracc = ErrorAccumulator()
    exporter._validate_analysis_kratio(analysis, options, erracc)

    assert len(erracc.exceptions) == 1
    assert len(erracc.warnings) == 0
