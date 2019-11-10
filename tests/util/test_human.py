#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.util.human import human_time, camelcase_to_words

# Globals and constants variables.


@pytest.mark.parametrize(
    "time_s,expected",
    [
        (5, "5 sec"),
        (65, "1 min 5 sec"),
        (60, "1 min"),
        (3665, "1 hr 1 min 5 sec"),
        (3660, "1 hr 1 min"),
        (3605, "1 hr 5 sec"),
        (3600, "1 hr"),
        (86400, "1 day"),
        (172800, "2 days"),
        (90000, "1 day 1 hr"),
        (90060, "1 day 1 hr 1 min"),
        (90061, "1 day 1 hr 1 min 1 sec"),
    ],
)
def test_human_time(time_s, expected):
    assert human_time(time_s) == expected


@pytest.mark.parametrize(
    "text,expected",
    [("AbcDef", "Abc Def"), ("AbcDEF", "Abc DEF"), ("AbcDeF", "Abc De F"),],
)
def testcamelcase_to_words(text, expected):
    assert camelcase_to_words(text) == expected
