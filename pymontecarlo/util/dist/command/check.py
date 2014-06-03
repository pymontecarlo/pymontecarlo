#!/usr/bin/env python
"""
================================================================================
:mod:`check` -- Check command for distutils
================================================================================

.. module:: check
   :synopsis: Check command for distutils

.. inheritance-diagram:: pymontecarlo.util.dist.command.check

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import re
from distutils.command.check import check as _check
from operator import attrgetter

# Third party modules.
from pkg_resources import iter_entry_points

# Local modules.

# Globals and constants variables.

class check(_check):

    def run(self):
        self.check_entrypoints()
        _check.run(self)

    def check_entrypoints(self):
        self.run_command('egg_info')
        self.check_gui_entrypoints()
        self.check_result_entrypoints()

    def check_gui_entrypoints(self):
        base_fileformat = 'pymontecarlo.fileformat.options.'
        base_gui = 'pymontecarlo.ui.gui.options.'
        modules = ['material', 'beam', 'geometry', 'detector', 'limit', 'result']
        for module in modules:
            eps = iter_entry_points(base_fileformat + module)
            expecteds = set(map(attrgetter('name'), eps))

            eps = iter_entry_points(base_gui + module)
            actuals = set(map(attrgetter('name'), eps))

            missings = expecteds - actuals
            if len(missings) > 0:
                self.warn("Missing %s GUI: %s" % (module, ', '.join(missings)))

    def check_result_entrypoints(self):
        eps = iter_entry_points('pymontecarlo.fileformat.options.detector')
        detectors = set(map(attrgetter('name'), eps))
        expecteds = {re.sub(r'Detector$', 'Result', d) for d in detectors}

        eps = iter_entry_points('pymontecarlo.fileformat.results.result')
        actuals = set(map(attrgetter('name'), eps))

        missings = expecteds - actuals
        if len(missings) > 0:
            self.warn("Missing result handler: %s" % (', '.join(sorted(missings)),))