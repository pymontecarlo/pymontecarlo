#!/usr/bin/env python
"""
================================================================================
:mod:`wrapper` -- Wrapper threads
================================================================================

.. module:: wrapper
   :synopsis: Wrapper threads

.. inheritance-diagram:: pymontecarlo.ui.gui.wrapper

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import time

# Third party modules.
from PySide.QtCore import Signal, QThread

# Local modules.
from pymontecarlo.fileformat.options.options import OptionsReader, OptionsWriter
from pymontecarlo.fileformat.results.results import ResultsReader, ResultsWriter

# Globals and constants variables.

class _MonitorableWrapperThread(QThread):

    resultReady = Signal(object)
    progressUpdated = Signal(float, str)
    exceptionRaised = Signal(Exception)

    def __init__(self, monitorable, args=(), kwargs=None):
        QThread.__init__(self)
        self._monitorable = monitorable
        self._args = args
        if kwargs is None:
            kwargs = {}
        self._kwargs = kwargs
        self._is_cancelled = False

    def _start_monitorable(self):
        raise NotImplementedError

    def run(self):
        self._start_monitorable()

        try:
            while self._monitorable.is_alive():
                self.progressUpdated.emit(self._monitorable.progress,
                                          self._monitorable.status)
                time.sleep(0.1)
        except Exception as ex:
            self.exceptionRaised.emit(ex)
            return
        finally:
            if not self._is_cancelled:
                self.progressUpdated.emit(self._monitorable.progress,
                                          self._monitorable.status)

        if not self._is_cancelled:
            try:
                result = self._monitorable.get()
            except Exception as ex:
                self.exceptionRaised.emit(ex)
            else:
                self.resultReady.emit(result)

    def cancel(self):
        self._is_cancelled = True
        self._monitorable.cancel()

class _OptionsReaderWrapperThread(_MonitorableWrapperThread):

    def __init__(self, filepath):
        monitorable = OptionsReader()
        args = (filepath,)
        _MonitorableWrapperThread.__init__(self, monitorable, args=args)

    def _start_monitorable(self):
        self._monitorable.read(*self._args, **self._kwargs)

class _OptionsWriterWrapperThread(_MonitorableWrapperThread):

    def __init__(self, options, filepath):
        monitorable = OptionsWriter()
        args = (options, filepath)
        _MonitorableWrapperThread.__init__(self, monitorable, args=args)

    def _start_monitorable(self):
        self._monitorable.write(*self._args, **self._kwargs)

class _ResultsReaderWrapperThread(_MonitorableWrapperThread):

    def __init__(self, filepath):
        monitorable = ResultsReader()
        args = (filepath,)
        _MonitorableWrapperThread.__init__(self, monitorable, args=args)

    def _start_monitorable(self):
        self._monitorable.read(*self._args, **self._kwargs)

class _ResultsWriterWrapperThread(_MonitorableWrapperThread):

    def __init__(self, results, filepath):
        monitorable = ResultsWriter()
        args = (results, filepath)
        _MonitorableWrapperThread.__init__(self, monitorable, args=args)

    def _start_monitorable(self):
        self._monitorable.write(*self._args, **self._kwargs)