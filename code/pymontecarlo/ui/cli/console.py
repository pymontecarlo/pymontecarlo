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
import logging
import warnings

# Third party modules.

# Local modules.

# Globals and constants variables.
COLOR_DEFAULT = 'default'
COLOR_RED = 'red'
COLOR_GREEN = 'green'
COLOR_BLUE = 'blue'
COLOR_YELLOW = 'yellow'

class ProgressBar(object):
    _BAR_TEMPLATE = 'Completed %i/%i | [%s%s] %i/100%% - %s'

    def __init__(self, console, total, fill_char='#', empty_char=' ', width=25):
        self._console = console
        self._total = total

        self._fill_char = fill_char
        self._empty_char = empty_char
        self._width = width

    def start(self):
        self._console.message('=' * self._console.width)
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
        text = self._create_bar_text(self._total, 1.0, 'Done')

        stream = self._console._stdout
        self._console._pre_print(stream, text, COLOR_GREEN)
        stream.write(text + '\n')
        self._console._post_print(stream, text, COLOR_GREEN)
        stream.flush()

        self._console.message('=' * self._console.width)

class ConsoleLoggingHandler(logging.Handler):
    def __init__(self, console, level=logging.NOTSET):
        logging.Handler.__init__(self, level)

        self._console = console

    def emit(self, record):
        try:
            msg = self.format(record)
            levelno = record.levelno

            if levelno >= logging.ERROR:
                self._console.error(msg)
            elif levelno >= logging.WARNING:
                self._console.warn(msg)
            elif levelno >= logging.INFO:
                self._console.info(msg)
            elif levelno >= logging.DEBUG:
                self._console.debug(msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

class _Console(object):
    _COLORS = {}

    def __init__(self, width=80, stdout=sys.stdout, stderr=sys.stderr):
        self._width = width
        self._stdout = stdout
        self._stderr = stderr

    @property
    def width(self):
        return self._width

    def init(self):
        # Redirect warnings
        def showwarning(message, category, filename, lineno, file=None, line=None):
            name = category.__name__.replace('Warning', '')
            self.warn('%s (%s)' % (message, name))
        warnings.showwarning = showwarning

        # Redirect logging
        logger = logging.getLogger()

        logger.handlers = []
        handler = ConsoleLoggingHandler(self)
        logger.addHandler(handler)

    def _pre_print(self, stream, text, color):
        pass

    def _print(self, stream, text, color=COLOR_DEFAULT):
        self._pre_print(stream, text, color)

        lines = []
        for line in textwrap.wrap(text, self.width, subsequent_indent='  '):
            lines.append(line.ljust(self.width - 1))
        stream.write('\n'.join(lines))

        self._post_print(stream, text, color)
        stream.write('\n')
        stream.flush()

    def _post_print(self, stream, text, color):
        pass

    def error(self, text):
        self._print(self._stderr, 'Error: ' + text, color=COLOR_RED)
        sys.exit(1)

    def warn(self, text):
        self._print(self._stderr, 'Warning: ' + text, color=COLOR_YELLOW)

    def info(self, text):
        self._print(self._stderr, 'Info: ' + text, color=COLOR_DEFAULT)

    def debug(self, text):
        self._print(self._stderr, 'Debug: ' + text, color=COLOR_BLUE)

    def message(self, text):
        self._print(self._stdout, text, color=COLOR_DEFAULT)

    def success(self, text):
        self._print(self._stdout, text, color=COLOR_GREEN)

    def close(self):
        # Reset warnings
        warnings.showwarning = warnings._show_warning

        # Reset logging basic configuration
        logger = logging.getLogger()
        logger.handlers = []
        logging.basicConfig()

        sys.exit(0)

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

        def close(self):
            windll.Kernel32.SetConsoleTextAttribute(self._handle, self._COLORS[COLOR_DEFAULT])
            _Console.close(self)

def create_console(width=80, stdout=sys.stdout, stderr=sys.stderr):
    if platform.system() == 'Windows':
        return WindowsConsole(width, stdout, stderr)
    else:
        return UnixConsole(width, stdout, stderr)
