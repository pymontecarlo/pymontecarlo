#!/usr/bin/env python
""" """

# Standard library modules.
import math

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.detector.base import DetectorBase
from pymontecarlo.options.options import OptionsBuilder
from pymontecarlo.options.analysis import PhotonIntensityAnalysis, KRatioAnalysis
from pymontecarlo.options.analysis.base import AnalysisBase
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.


@pytest.fixture
def builder():
    return OptionsBuilder()


def test_options(options):
    assert options.beam.energy_eV == pytest.approx(15e3, abs=1e-4)

    assert len(options.find_detectors(PhotonDetector)) == 1
    assert len(options.find_detectors(DetectorBase)) == 1

    assert len(options.find_analyses(PhotonIntensityAnalysis)) == 1
    assert len(options.find_analyses(AnalysisBase)) == 1

    detector = options.detectors[0]
    assert len(options.find_analyses(PhotonIntensityAnalysis, detector)) == 1

    assert len(options.find_analyses(DetectorBase)) == 0


def test_options_hdf5(options, tmp_path):
    testutil.assert_convert_parse_hdf5(options, tmp_path)


def test_options_copy(options):
    testutil.assert_copy(options)


def test_options_pickle(options):
    testutil.assert_pickle(options)


def test_options_series(options, seriesbuilder):
    options.convert_series(seriesbuilder)
    assert len(seriesbuilder.build()) == 16


def test_options_document(options, documentbuilder):
    options.convert_document(documentbuilder)
    document = documentbuilder.build()
    assert testutil.count_document_nodes(document) == 14


#    from pymontecarlo.formats.document import publish_html
#    with open('/tmp/options.html', 'wb') as fp:
#        fp.write(publish_html(documentbuilder))


def test_optionsbuilder_single(builder, options):
    builder.add_program(options.program)
    builder.add_beam(options.beam)
    builder.add_sample(options.sample)

    assert len(builder) == 1
    assert len(builder.build()) == 1


def test_optionsbuilder_sameoption(builder, options):
    builder.add_program(options.program)
    builder.add_program(options.program)
    builder.add_beam(options.beam)
    builder.add_beam(options.beam)
    builder.add_sample(options.sample)
    builder.add_sample(options.sample)

    assert len(builder) == 1
    assert len(builder.build()) == 1


def test_optionsbuilder_kratioanalysis(builder, options):
    builder.add_program(options.program)
    builder.add_beam(options.beam)
    builder.add_sample(options.sample)

    det = PhotonDetector("det", math.radians(50))
    builder.add_analysis(KRatioAnalysis(det))

    assert len(builder) == 1
    assert len(builder.build()) == 2


def test_optionsbuilder_kratioanalysis_with_photonintensityanalysis(builder, options):
    builder.add_program(options.program)
    builder.add_beam(options.beam)
    builder.add_sample(options.sample)

    det = PhotonDetector("det", math.radians(50))
    builder.add_analysis(KRatioAnalysis(det))
    builder.add_analysis(PhotonIntensityAnalysis(det))

    assert len(builder) == 1
    assert len(builder.build()) == 2


def test_optionsbuilder_twokratioanalysis(builder, options):
    builder.add_program(options.program)
    builder.add_beam(options.beam)
    builder.add_sample(options.sample)

    det = PhotonDetector("det", math.radians(50))
    builder.add_analysis(KRatioAnalysis(det))

    det = PhotonDetector("det2", math.radians(55))
    builder.add_analysis(KRatioAnalysis(det))

    assert len(builder) == 2
    assert len(builder.build()) == 4
