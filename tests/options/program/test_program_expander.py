#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.program.expander import (
    expand_to_single,
    expand_analyses_to_single_detector,
)
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.analysis import PhotonIntensityAnalysis, KRatioAnalysis

# Globals and constants variables.


class MockA:
    pass


class MockB:
    pass


def testexpand_to_single():
    obj1 = MockA()
    obj2 = MockA()
    obj3 = MockB()
    objects = [obj1, obj2, obj3]
    combinations = expand_to_single(objects)

    assert len(combinations) == 2

    combination = combinations[0]
    assert len(combination) == 2
    assert obj1 in combination
    assert obj3 in combination

    combination = combinations[1]
    assert len(combination) == 2
    assert obj2 in combination
    assert obj3 in combination


def testexpand_analyses_to_single_detector():
    det1 = PhotonDetector("det1", 0.1)
    det2 = PhotonDetector("det2", 3.3)

    analyses = [
        PhotonIntensityAnalysis(det1),
        PhotonIntensityAnalysis(det2),
        KRatioAnalysis(det1),
        KRatioAnalysis(det2),
    ]

    combinations = expand_analyses_to_single_detector(analyses)
    assert len(combinations) == 2

    combinations = expand_to_single(analyses)
    assert len(combinations) == 4
