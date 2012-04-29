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
import os
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
COLOR_PURPLE = 'purple'

class ProgressBar(object):
    _BAR_TEMPLATE = 'Completed %i/%i | [%s%s] %i/100%% - %s'

    def __init__(self, console, total, fill_char='#', empty_char=' ', width=25):
        self._console = console
        self._total = total

        self._fill_char = fill_char
        self._empty_char = empty_char
        self._width = width

    def start(self):
        self._console.print_message('=' * self._console.width)
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

        self._console.print_message('=' * self._console.width)

class ConsoleLoggingHandler(logging.Handler):
    def __init__(self, console, level=logging.NOTSET):
        logging.Handler.__init__(self, level)

        self._console = console

    def emit(self, record):
        try:
            msg = self.format(record)
            levelno = record.levelno

            if levelno >= logging.ERROR:
                self._console.print_error(msg)
            elif levelno >= logging.WARNING:
                self._console.print_warn(msg)
            elif levelno >= logging.INFO:
                self._console.print_info(msg)
            elif levelno >= logging.DEBUG:
                self._console.print_debug(msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

class _Console(object):
    _COLORS = {}
    _PROMPT_PREFIX = "> "

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

    def _print(self, stream, text, color=COLOR_DEFAULT,
               eol=True, wrap=True, fill=True):
        self._pre_print(stream, text, color)

        # Wrap
        lines = []
        if wrap:
            for line in textwrap.wrap(text, self.width, subsequent_indent='  '):
                lines.append(line)

            if text.endswith((' ', '\t')): lines[-1] += ' '
        else:
            lines.append(text)

        # Fill with white space
        if fill:
            for i in range(len(lines)):
                lines[i] = lines[i].ljust(self.width - 1)

        # Write
        stream.write('\n'.join(lines))

        self._post_print(stream, text, color)
        if eol: stream.write('\n')
        stream.flush()

    def _post_print(self, stream, text, color):
        pass

    def print_error(self, text, exit=True):
        self._print(self._stderr, 'Error: ' + text, color=COLOR_RED)
        if exit: self.close(1)

    def print_warn(self, text):
        self._print(self._stderr, 'Warning: ' + text, color=COLOR_YELLOW)

    def print_info(self, text):
        self._print(self._stderr, 'Info: ' + text, color=COLOR_DEFAULT)

    def print_debug(self, text):
        self._print(self._stderr, 'Debug: ' + text, color=COLOR_BLUE)

    def print_message(self, text):
        self._print(self._stdout, text, color=COLOR_DEFAULT)

    def print_success(self, text):
        self._print(self._stdout, text, color=COLOR_GREEN)

    def print_line(self):
        self._print(self._stdout, "-" * self._width)

    def _prompt(self, question, default=None, validators=[]):
        text = self._PROMPT_PREFIX + question
        if default: text += ' [%s]' % default
        text += ": "

        while True:
            self._print(self._stdout, text, COLOR_PURPLE, eol=False, fill=False)
            answer = raw_input() or default

            if answer is None: answer = ''
            answer = answer.strip()

            try:
                for validator in reversed(validators):
                    validator(answer)
            except Exception as ex:
                self.print_error(str(ex), False)
                continue

            break

        return answer

    def prompt_text(self, question, default=None, validators=[]):
        # Validators
        def _nonempty(answer):
            if not answer:
                raise ValueError, 'Please enter some text.'
        validators.append(_nonempty)

        # Prompt
        return self._prompt(question, default, validators)

    def prompt_boolean(self, question, default=None, validators=[]):
        # Validators
        def _boolean(answer):
            if answer.upper() not in ('Y', 'YES', 'N', 'NO'):
                raise ValueError, "Please enter either 'y' or 'n'"
        validators.append(_boolean)

        # Default
        if default is not None:
            default = 'y' if default else 'n'

        # Prompt
        answer = self.prompt_text(question, default, validators)
        return answer.upper() in ('Y', 'YES')

    def prompt_file(self, question, default=None, should_exist=True, validators=[]):
        # Validators
        def _exists(answer):
            if should_exist and not os.path.isfile(answer):
                raise ValueError, "Please enter an existing file"
        validators.append(_exists)

        # Prompt
        answer = self.prompt_text(question, default, validators)

        return os.path.abspath(answer)

    def prompt_directory(self, question, default=None, should_exist=True, validators=[]):
        # Validators
        def _exists(answer):
            if should_exist and not os.path.isdir(answer):
                raise ValueError, "Please enter an existing file"
        validators.append(_exists)

        # Prompt
        answer = self.prompt_text(question, default, validators)

        return os.path.abspath(answer)

    def prompt_float(self, question, default=None, validators=[]):
        # Validators
        def _float(answer):
            try:
                answer = float(answer)
            except ValueError:
                raise ValueError, "Cannot convert %s to float" % answer
        validators.append(_float)

        if default is not None: default = str(default)

        # Prompt
        return float(self.prompt_text(question, default, validators))

    def prompt_int(self, question, default=None, validators=[]):
        # Validators
        def _int(answer):
            try:
                answer = int(answer)
            except ValueError:
                raise ValueError, "Cannot convert %s to integer" % answer
        validators.append(_int)

        if default is not None: default = str(default)

        # Prompt
        return int(self.prompt_text(question, default, validators))

    def close(self, retcode=0):
        # Reset warnings
        warnings.showwarning = warnings._show_warning

        # Reset logging basic configuration
        logger = logging.getLogger()
        logger.handlers = []
        logging.basicConfig()

        sys.exit(retcode)

class UnixConsole(_Console):
    _COLORS = {COLOR_DEFAULT: 0, COLOR_RED: 31, COLOR_GREEN: 32,
               COLOR_BLUE: 34, COLOR_YELLOW: 33, COLOR_PURPLE: 35}

    def _pre_print(self, stream, text, color):
        stream.write("\033[%dm\033[1m" % self._COLORS[color])

    def _post_print(self, stream, text, color):
        stream.write("\033[0m")

if platform.system() == 'Windows':
    from ctypes import windll, c_ulong

    class WindowsConsole(_Console):
        _COLORS = {COLOR_DEFAULT: 15, COLOR_RED: 12, COLOR_GREEN: 10,
                   COLOR_BLUE: 9, COLOR_YELLOW: 14, COLOR_PURPLE: 15}
        #FIXME: Find purple color in Windows

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
