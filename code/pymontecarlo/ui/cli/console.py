#!/usr/bin/env python
"""
================================================================================
:mod:`console` -- Console to interact with the command line interface
================================================================================

.. module:: console
   :synopsis: Console to interact with the command line interface

.. inheritance-diagram:: pymontecarlo.ui.cli.console

Generic interface to interact with the command line.
A console implements easy functions to print error, warning, information 
messages as well as to retrieve data from the user.

To ensure that the right console is used for the operating system, the
method :meth:`create_console` should be called instead of the actual console
constructor.
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
    _BAR_TEMPLATE = 'Completed %i/%i | [%s%s] %i%% - %s'

    def __init__(self, console, total, fill_char='#', empty_char=' ', width=25):
        """
        Creates a progress bar to show the progress of task(s) in the command
        line.
        The progress bar displays two progresses: the number of tasks completed
        and the progress of each task.
        There is an example of the progress bar output::
        
          Completed 1/5 | [###########             ] 45%% - Running task 1
        
        Once created and initialized, the method :meth:`update` should be call
        to redraws the progress bar in the command line.
        
        :arg console: console where the progress bar will be written
        :arg total: total number of tasks
        :arg fill_char: character used in the bar of the progress bar
        :arg empty_char: character used to fill the progress bar
        :arg width: width the progress bar
        """
        self._console = console
        self._total = total

        self._fill_char = fill_char
        self._empty_char = empty_char
        self._width = width

    def start(self):
        """
        Initializes this progress bar.
        This method must be called before calling :meth:`update`
        """
        self._console.print_message('=' * self._console.width)
        self.update(0, 0, 'Start')

    def _create_bar_text(self, counter, progress, status):
        """
        Constructs the text for this progress bar.
        
        :arg counter: number of completed tasks
        :arg progress: progress of the running task (0.0 to 1.0)
        :arg status: status of the running task
        """
        if progress < 0: progress = 0.0
        if progress > 1: progress = 1.0

        x = int(progress * self._width)
        fill = self._fill_char * x
        empty = self._empty_char * (self._width - x)

        text = self._BAR_TEMPLATE % (counter, self._total, fill, empty,
                                     progress * 100, status)
        text = text[:self._console.width - 1].ljust(self._console.width - 1)

        return text

    def update(self, counter, progress, status):
        """
        Updates the progress and status of this progress bar.
        
        :arg counter: number of completed tasks
        :arg progress: progress of the running task (0.0 to 1.0)
        :arg status: status of the running task
        """
        text = self._create_bar_text(counter, progress, status)
        stream = self._console._stdout
        stream.write(text + "\r")
        stream.flush()

    def close(self):
        """
        Closes this progress bar.
        The progress bar will appear in green with *Done* as the status message.
        """
        text = self._create_bar_text(self._total, 1.0, 'Done')

        stream = self._console._stdout
        self._console._pre_print(stream, text, COLOR_GREEN)
        stream.write(text + '\n')
        self._console._post_print(stream, text, COLOR_GREEN)
        stream.flush()

        self._console.print_message('=' * self._console.width)

class ConsoleLoggingHandler(logging.Handler):
    """
    Special logging handler to redirect log messages to the console.
    """

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
        """
        Creates a new console.
        The method :meth:`init` should be called to initialize the console
        after it is created.
        
        :arg width: number of characters in one line [default: 80]
            Text exceeding this number of characters will be wrapped to multiple
            lines.
        :arg stdout: where to write the output [default: ``sys.stdout``]
        :arg stderr: where to write the error output [default: ``sys.stderr``]
        """
        self._width = width
        self._stdout = stdout
        self._stderr = stderr

    @property
    def width(self):
        """
        Maximum number of characters in one line.
        """
        return self._width

    def init(self):
        """
        Initializes the console. 
        This method grabs the control of warnings and logging. 
        All warnings or log message are redirected to the console.
        """
        # Redirect warnings
        def showwarning(message, category, filename, lineno, file=None, line=None):
            name = category.__name__.replace('Warning', '')
            self.print_warn('%s (%s)' % (message, name))
        warnings.showwarning = showwarning

        # Redirect logging
        logger = logging.getLogger()

        logger.handlers = []
        handler = ConsoleLoggingHandler(self)
        logger.addHandler(handler)

    def _pre_print(self, stream, text, color):
        """
        Performs pre-processing before the method : meth:`_print` is called.
        """
        pass

    def _print(self, stream, text, color=COLOR_DEFAULT,
               eol=True, wrap=True, fill=True):
        """
        Prints a text.
        
        :arg stream: where to write the text (usually, stdout or stderr)
        :arg text: text to print
        :arg color: color of the text [default: COLOR_DEFAULT]
        :arg eol: whether to add a carriage return after writing the text
            [default: ``True``]
        :arg wrap: whether to wrap the text [default: ``True``]
        :arg fill: whether to add whitespace at the end of each line up to
            the console's width [default: ``True``]
        """
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
        """
        Performs post-processing after the method : meth:`_print` was called.
        """
        pass

    def print_error(self, text, exit=True):
        """
        Prints an error message in red.
        
        :arg exit: whether to exit the program after writing the error message
            [default: ``True``]
        """
        self._print(self._stderr, 'Error: ' + text, color=COLOR_RED)
        if exit: self.close(1)

    def print_warn(self, text):
        """
        Prints a warning message in yellow.
        """
        self._print(self._stderr, 'Warning: ' + text, color=COLOR_YELLOW)

    def print_info(self, text):
        """
        Prints a information message.
        """
        self._print(self._stderr, 'Info: ' + text, color=COLOR_DEFAULT)

    def print_debug(self, text):
        """
        Prints a debug message in blue.
        """
        self._print(self._stderr, 'Debug: ' + text, color=COLOR_BLUE)

    def print_message(self, text):
        """
        Prints a message.
        """
        self._print(self._stdout, text, color=COLOR_DEFAULT)

    def print_success(self, text):
        """
        Prints a successful message in green.
        """
        self._print(self._stdout, text, color=COLOR_GREEN)

    def print_line(self):
        """
        Prints a separating line.
        """
        self._print(self._stdout, "-" * self._width)

    def _prompt(self, question, default=None, validators=[]):
        """
        Prints a question and retrieve the answer.
        If no answer is given and a default value is given, the default value
        is returned.
        Otherwise, an empty string is returned.
        
        The answer can be validated with validators.
        A validator is a function taking the answer as its only argument.
        If the answer is invalid, the validator should raise an exception.
        In this situation, the question will be asked again until a valid
        answer is given.
        
        :arg question: question to ask
        :arg default: default value when no answer is given
        :arg validators: :class:`list` of functions
        """
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
        """
        Prompts for a textual value. 
        Any answer is accepted, except an empty string.
        
        :arg question: question to ask
        :arg default: default value when no answer is given
        :arg validators: :class:`list` of functions
        """
        # Validators
        def _nonempty(answer):
            if not answer:
                raise ValueError, 'Please enter some text.'
        validators.append(_nonempty)

        # Prompt
        return self._prompt(question, default, validators)

    def prompt_boolean(self, question, default=None, validators=[]):
        """
        Prompts for a boolean value. 
        Only the following answers are accepted: ``y``, ``yes``, ``n``, ``no``
        and their uppercase equivalents.
        
        :arg question: question to ask
        :arg default: default value when no answer is given (either ``True`` or
            ``False``)
        :arg validators: :class:`list` of functions
        
        :rtype: :class:`bool`
        """
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
        """
        Prompts for a path to a file.
        If the ``should_exist`` flag is ``True``, the answer is valid if the
        specified file exists.
        Otherwise, any non-empty answer is accepted. 
        
        :arg question: question to ask
        :arg default: default path when no answer is given
        :arg should_exist: whether to check if the specified path is a valid
            path to a file [default: ``True``]
        :arg validators: :class:`list` of functions
        """
        # Validators
        def _exists(answer):
            if should_exist and not os.path.isfile(answer):
                raise ValueError, "Please enter an existing file"
        validators.append(_exists)

        # Prompt
        answer = self.prompt_text(question, default, validators)

        return os.path.abspath(answer)

    def prompt_directory(self, question, default=None, should_exist=True, validators=[]):
        """
        Prompts for a path to a directory.
        If the ``should_exist`` flag is ``True``, the answer is valid if the
        specified directory exists.
        Otherwise, any non-empty answer is accepted. 
        
        :arg question: question to ask
        :arg default: default path when no answer is given
        :arg should_exist: whether to check if the specified path is a valid
            path to a directory [default: ``True``]
        :arg validators: :class:`list` of functions
        """
        # Validators
        def _exists(answer):
            if should_exist and not os.path.isdir(answer):
                raise ValueError, "Please enter an existing file"
        validators.append(_exists)

        # Prompt
        answer = self.prompt_text(question, default, validators)

        return os.path.abspath(answer)

    def prompt_float(self, question, default=None, validators=[]):
        """
        Prompts for a float value. 
        An answer is valid if it can be converted to a float.
        
        :arg question: question to ask
        :arg default: default value when no answer is given 
        :arg validators: :class:`list` of functions
        
        :rtype: :class:`float`
        """
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
        """
        Prompts for a integer value. 
        An answer is valid if it can be converted to a integer.
        
        :arg question: question to ask
        :arg default: default value when no answer is given 
        :arg validators: :class:`list` of functions
        
        :rtype: :class:`int`
        """
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
        """
        Closes the console and the program.
        It resets the logging and warnings settings to the default settings.
        
        :arg retcode: return code sent to ``sys.exit``
        """
        # Reset warnings
        warnings.showwarning = warnings._show_warning

        # Reset logging basic configuration
        logger = logging.getLogger()
        logger.handlers = []
        logging.basicConfig()

        sys.exit(retcode)

class UnixConsole(_Console):
    """
    Console for UNIX-like platform.
    """

    _COLORS = {COLOR_DEFAULT: 0, COLOR_RED: 31, COLOR_GREEN: 32,
               COLOR_BLUE: 34, COLOR_YELLOW: 33, COLOR_PURPLE: 35}

    def _pre_print(self, stream, text, color):
        stream.write("\033[%dm\033[1m" % self._COLORS[color])

    def _post_print(self, stream, text, color):
        stream.write("\033[0m")

if platform.system() == 'Windows':
    from ctypes import windll, c_ulong

    class WindowsConsole(_Console):
        """
        Console for Windows platform.
        """

        _COLORS = {COLOR_DEFAULT: 15, COLOR_RED: 12, COLOR_GREEN: 10,
                   COLOR_BLUE: 9, COLOR_YELLOW: 14, COLOR_PURPLE: 13}

        def __init__(self, width=80, stdout=sys.stdout, stderr=sys.stderr):
            _Console.__init__(self, width, stdout, stderr)

            windll.Kernel32.GetStdHandle.restype = c_ulong
            self._handle = windll.Kernel32.GetStdHandle(c_ulong(0xfffffff5))

        def _pre_print(self, stream, text, color):
            windll.Kernel32.SetConsoleTextAttribute(self._handle, self._COLORS[color])

        def _post_print(self, stream, text, color):
            windll.Kernel32.SetConsoleTextAttribute(self._handle, self._COLORS[COLOR_DEFAULT])

        def close(self, retcode=0):
            windll.Kernel32.SetConsoleTextAttribute(self._handle, self._COLORS[COLOR_DEFAULT])
            _Console.close(self, retcode)

def create_console(width=80, stdout=sys.stdout, stderr=sys.stderr):
    """
    Creates a console based on the platform.
    
    :arg width: number of characters in one line [default: 80]
        Text exceeding this number of characters will be wrapped to multiple
        lines.
    :arg stdout: where to write the output [default: ``sys.stdout``]
    :arg stderr: where to write the error output [default: ``sys.stderr``]
    """
    if platform.system() == 'Windows':
        return WindowsConsole(width, stdout, stderr)
    else:
        return UnixConsole(width, stdout, stderr)
