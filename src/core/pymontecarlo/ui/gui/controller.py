#!/usr/bin/env python
"""
================================================================================
:mod:`controller` -- Controller
================================================================================

.. module:: controller
   :synopsis: Controller

.. inheritance-diagram:: pymontecarlo.ui.gui.controller

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
from PySide.QtCore import QObject, Signal, QThread

# Local modules.
from pymontecarlo.options.options import Options

from pymontecarlo.fileformat.options.options import OptionsReader, OptionsWriter

from pymontecarlo.settings import get_settings

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

class Controller(QObject):

    optionsNewRequested = Signal()

    optionsOpen = Signal(str)
    optionsOpenCancel = Signal()
    optionsOpenProgress = Signal(float, str)
    optionsOpenException = Signal(Exception)
    optionsOpened = Signal(Options, str)

    optionsAddRequested = Signal(Options)
    optionsAdded = Signal(str, Options)
    optionsRemoveRequested = Signal(str)
    optionsRemoved = Signal(str)
    optionsModifyRequested = Signal(str)
    optionsModified = Signal(str, Options)

    optionsSaveRequested = Signal(str)
    optionsSaveAsRequested = Signal(str)
    optionsSave = Signal(str, str)
    optionsSaveCancel = Signal()
    optionsSaveProgress = Signal(float, str)
    optionsSaveException = Signal(Exception)
    optionsSaved = Signal(str, str)

    beamDisplayRequested = Signal(str)
    beamDisplayed = Signal(str)
    beamDisplayClosed = Signal(str)

    geometryDisplayRequested = Signal(str)
    geometryDisplayed = Signal(str)
    geometryDisplayClosed = Signal(str)

    detectorsDisplayRequested = Signal(str)
    detectorsDisplayed = Signal(str)
    detectorsDisplayClosed = Signal(str)

    limitsDisplayRequested = Signal(str)
    limitsDisplayed = Signal(str)
    limitsDisplayClosed = Signal(str)

    modelsDisplayRequested = Signal(str)
    modelsDisplayed = Signal(str)
    modelsDisplayClosed = Signal(str)

    def __init__(self):
        QObject.__init__(self) # Required to activate signals

        # Variables
        self._list_options = {}
        self._options_edited = {}
        self._options_filepath = {}

        self._reader_thread = None
        self._writer_thread = None

        # Signals
        self.optionsOpen.connect(self._onOptionsOpen)
        self.optionsOpenCancel.connect(self._onOptionsOpenCancel)
        self.optionsOpenException.connect(self._onOptionsOpenException)
        self.optionsOpened.connect(self._onOptionsOpened)

        self.optionsSave.connect(self._onOptionsSave)
        self.optionsSaveCancel.connect(self._onOptionsSaveCancel)
        self.optionsSaveException.connect(self._onOptionsSaveException)
        self.optionsSaved.connect(self._onOptionsSaved)

        self.optionsAddRequested.connect(self._onOptionsAddRequested)
        self.optionsRemoveRequested.connect(self._onOptionsRemoveRequested)
        self.optionsModified.connect(self._onOptionsModified)

    def _onOptionsOpen(self, filepath):
        self._reader_thread = _OptionsReaderWrapperThread(filepath)
        self._reader_thread.resultReady.connect(lambda ops, f=filepath: self.optionsOpened.emit(ops, f))
        self._reader_thread.progressUpdated.connect(self.optionsOpenProgress)
        self._reader_thread.exceptionRaised.connect(self.optionsOpenException)
        self._reader_thread.start()

    def _onOptionsOpenCancel(self):
        if self._reader_thread is None:
            return
        self._reader_thread.cancel()
        self._reader_thread.quit()
        self._reader_thread.wait()

    def _onOptionsOpenException(self):
        self._reader_thread.quit()
        self._reader_thread.wait()

    def _onOptionsOpened(self, options, filepath):
        self._reader_thread.quit()
        self._reader_thread.wait()
        self._reader_thread = None

        self._options_filepath[options.uuid] = filepath
        self.optionsAddRequested.emit(options)

    def _onOptionsSave(self, uid, filepath):
        options = self._list_options[uid]
        self._writer_thread = _OptionsWriterWrapperThread(options, filepath)
        self._writer_thread.resultReady.connect(lambda f, u=uid: self.optionsSaved.emit(u, f))
        self._writer_thread.progressUpdated.connect(self.optionsSaveProgress)
        self._writer_thread.exceptionRaised.connect(self.optionsSaveException)
        self._writer_thread.start()

    def _onOptionsSaveCancel(self):
        if self._writer_thread is None:
            return
        self._writer_thread.cancel()
        self._writer_thread.quit()
        self._writer_thread.wait()

    def _onOptionsSaveException(self):
        self._writer_thread.quit()
        self._writer_thread.wait()

    def _onOptionsSaved(self, uid, filepath):
        self._writer_thread.quit()
        self._writer_thread.wait()
        self._writer_thread = None
        self._options_edited[uid] = False
        self._options_filepath[uid] = filepath

    def _onOptionsAddRequested(self, options):
        uid = options.uuid
        if uid in self._list_options:
            raise ValueError('Already opened')

        self._list_options[uid] = options
        self._options_edited[uid] = False
        self.optionsAdded.emit(uid, options)

    def _onOptionsRemoveRequested(self, uid):
        self._list_options.pop(uid)
        self._options_edited.pop(uid, None)
        self._options_filepath.pop(uid, None)
        self.optionsRemoved.emit(uid)

    def _onOptionsModified(self, uid, options):
        self._list_options[uid] = options
        self._options_edited[uid] = True

    def settings(self):
        return get_settings()

    def options(self, uid):
        return self._list_options[uid]

    def isOptionsEdited(self, uid):
        return self._options_edited.get(uid, False)

    def optionsFilepath(self, uid):
        return self._options_filepath.get(uid)
