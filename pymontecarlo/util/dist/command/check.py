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

    def _get_entrypoints(self, group):
        entrypoints = set()
        for ep in iter_entry_points(group):
            try:
                ep.load()
            except:
                self.warn("Cannot open %s from %s" % (ep.name, group))
            else:
                entrypoints.add(ep.name)
        return entrypoints

    def _check_gui_entrypoints(self, group1, group2):
        expecteds = self._get_entrypoints(group1)
        actuals = self._get_entrypoints(group2)

        missings = expecteds - actuals
        if len(missings) > 0:
            self.warn("Missing GUI: %s" % (', '.join(missings),))

    def check_gui_entrypoints(self):
        base_fileformat = 'pymontecarlo.fileformat.options.'
        base_gui = 'pymontecarlo.ui.gui.options.'
        modules = ['material', 'beam', 'geometry', 'detector', 'limit', 'result']
        for module in modules:
            self._check_gui_entrypoints(base_fileformat + module,
                                        base_gui + module)

        self._check_gui_entrypoints('pymontecarlo.fileformat.results.result',
                                    'pymontecarlo.ui.gui.results.result')

    def check_result_entrypoints(self):
        expecteds = {re.sub(r'Detector$', 'Result', d)
                     for d in self._get_entrypoints('pymontecarlo.fileformat.options.detector')}
        actuals = self._get_entrypoints('pymontecarlo.fileformat.results.result')
        missings = expecteds - actuals
        if len(missings) > 0:
            self.warn("Missing result handler: %s" % (', '.join(sorted(missings)),))
