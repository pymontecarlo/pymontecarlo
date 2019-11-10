#!/usr/bin/env python
""" """

# Standard library modules.
import sys
import subprocess

# Third party modules.

# Local modules.

# Globals and constants variables.


def test__main__():
    args = [sys.executable, "-m", "pymontecarlo"]
    process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = process.stdout.decode("ascii")
    assert out.startswith("usage: pymontecarlo")
