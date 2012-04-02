#!/usr/bin/env python
"""
================================================================================
:mod:`console` -- Console to interact with the command line interface
================================================================================

.. module:: console
   :synopsis: Console to interact with the command line interface

.. inheritance-diagram:: pymontecarlo.ui.cli.console

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import sys
import platform
import textwrap

# Third party modules.

# Local modules.

# Globals and constants variables.
COLOR_DEFAULT = 'default'
COLOR_RED = 'red'
COLOR_GREEN = 'green'
COLOR_BLUE = 'blue'
COLOR_YELLOW = 'yellow'

class ProgressBar(object):
    _BAR_TEMPLATE = 'Simulation %i/%i: [%s%s] %i/100%% - %s'

    def __init__(self, console, total, fill_char='#', empty_char=' ', width=25):
        self._console = console
        self._total = total

        self._fill_char = fill_char
        self._empty_char = empty_char
        self._width = width

    def start(self):
        self.update(0, 0, 'Start')

    def _create_bar_text(self, counter, progress, status):
        x = int(progress * self._width)
        fill = self._fill_char * x
        empty = self._empty_char * (self._width - x)

        text = self._BAR_TEMPLATE % (counter, self._total, fill, empty,
                                     progress * 100, status)
        text = text[:self._console.width - 1].ljust(self._console.width - 1)

        return text

    def update(self, counter, progress, status):
        text = self._create_bar_text(counter, progress, status)
        stream = self._console._stdout
        stream.write(text + "\r")
        stream.flush()

    def close(self):
        text = self._create_bar_text(self._total, 1.0, 'Completed')

        stream = self._console._stdout
        self._console._pre_print(stream, text, COLOR_GREEN)
        stream.write(text + '\n')
        self._console._post_print(stream, text, COLOR_GREEN)
        stream.flush()

class _Console(object):
    _COLORS = {}

    def __init__(self, width=80, stdout=sys.stdout, stderr=sys.stderr):
        self._width = width
        self._stdout = stdout
        self._stderr = stderr

    @property
    def width(self):
        return self._width

    def _pre_print(self, stream, text, color):
        pass

    def _print(self, stream, text, color=COLOR_DEFAULT):
        self._pre_print(stream, text, color)

        out = '\n'.join(textwrap.wrap(text, self.width, subsequent_indent='  '))
        stream.write(out)

        self._post_print(stream, text, color)
        stream.write('\n')

    def _post_print(self, stream, text, color):
        pass

    def error(self, text):
        self._print(self._stderr, text, color=COLOR_RED)
        sys.exit(1)

    def warn(self, text):
        self._print(self._stderr, text, color=COLOR_YELLOW)

    def info(self, text):
        self._print(self._stdout, text, color=COLOR_DEFAULT)

    def success(self, text):
        self._print(self._stdout, text, color=COLOR_GREEN)

class UnixConsole(_Console):
    _COLORS = {COLOR_DEFAULT: 0, COLOR_RED: 31, COLOR_GREEN: 32,
               COLOR_BLUE: 34, COLOR_YELLOW: 33}

    def _pre_print(self, stream, text, color):
        stream.write("\033[%dm\033[1m" % self._COLORS[color])

    def _post_print(self, stream, text, color):
        stream.write("\033[0m")

if platform.system() == 'Windows':
    from ctypes import windll, c_ulong

    class WindowsConsole(_Console):
        _COLORS = {COLOR_DEFAULT: 15, COLOR_RED: 12, COLOR_GREEN: 10,
                   COLOR_BLUE: 9, COLOR_YELLOW: 14}

        def __init__(self, width=80, stdout=sys.stdout, stderr=sys.stderr):
            _Console.__init__(self, width, stdout, stderr)

            windll.Kernel32.GetStdHandle.restype = c_ulong
            self._handle = windll.Kernel32.GetStdHandle(c_ulong(0xfffffff5))

        def _pre_print(self, stream, text, color):
            windll.Kernel32.SetConsoleTextAttribute(self._handle, self._COLORS[color])

        def _post_print(self, stream, text, color):
            windll.Kernel32.SetConsoleTextAttribute(self._handle, self._COLORS[COLOR_DEFAULT])

def create_console(width=80, stdout=sys.stdout, stderr=sys.stderr):
    if platform.system() == 'Windows':
        return WindowsConsole(width, stdout, stderr)
    else:
        return UnixConsole(width, stdout, stderr)
