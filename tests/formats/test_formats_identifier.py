#!/usr/bin/env python
""" """

# Standard library modules.
import copy

# Third party modules.

# Local modules.
from pymontecarlo.formats.identifier import create_identifier, create_identifiers

# Globals and constants variables.


def test_create_identifier(options):
    identifier = create_identifier(options)
    assert len(identifier) == 243


def test_create_identifiers(options):
    options2 = copy.deepcopy(options)
    options2.beam.energy_eV = 20e3
    identifiers = create_identifiers([options, options2])
    assert len(identifiers) == 2
