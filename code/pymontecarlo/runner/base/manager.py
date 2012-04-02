#!/usr/bin/env python
"""
================================================================================
:mod:`manager` -- Runner manager
================================================================================

.. module:: manager
   :synopsis: Runner manager

.. inheritance-diagram:: manager

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import platform

# Third party modules.

# Local modules.
from pymontecarlo.runner.base.runner import Runner

# Globals and constants variables.

PLATFORM_WINDOWS = 'Windows'
PLATFORM_MACOS = 'MacOS'
PLATFORM_LINUX = 'Linux'
ALL_PLATFORMS = [PLATFORM_WINDOWS, PLATFORM_MACOS, PLATFORM_LINUX]

class _RunnerManager:
    def __init__(self):
        self._runners = {}
        self._platforms = {}

    def register(self, flag, klass, platforms):
        if not issubclass(klass, Runner):
            raise ValueError, 'The class (%s) must be a subclass of Runner.' % \
                klass.__name__

        if flag in self._runners and self._runners.get(flag) != klass:
            raise ValueError, 'A class (%s) is already registered with the flag (%s).' % \
                (self._runners[flag].__name__, flag)

        self._runners[flag] = klass

        for platform in platforms:
            if platform not in ALL_PLATFORMS:
                raise ValueError, 'Unknown platform (%s). Must be either %s' % \
                        (platform, ', '.join(ALL_PLATFORMS))
            self._platforms.setdefault(platform, []).append(flag)

    def get_runners(self, platform):
        """
        Returns the tags of the runner supported by the specified platform.
        
        :arg platform: system platform
        """
        return self._platforms.get(platform, [])

    def get_runner(self, flag):
        """
        Returns the runner class for the specified flag.
        Raises :exc:`ValueError` if no class is associated with this tag.
        
        :arg flag: flag associated with a runner
        
        :return: runner
        """
        if flag not in self._runners:
            raise ValueError, 'No loader found for flag (%s). Please register it first.' % flag
        return self._runners[flag]

RunnerManager = _RunnerManager()
