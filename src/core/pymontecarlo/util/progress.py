#!/usr/bin/env python
"""
================================================================================
:mod:`progress` -- Track progress of task(s)
================================================================================

.. module:: progress
   :synopsis: Track progress of task

.. inheritance-diagram:: pymontecarlo.util.progress

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import threading
from operator import attrgetter

# Third party modules.

# Local modules.

# Globals and constants variables.

class Task:

    def __init__(self, alias):
        """
        Creates a new task.
        
        :arg alias: alias of task
        """
        self._alias = str(alias)
        self._progress = 0.0
        self._status = ''
        self._lock = threading.RLock()

    def __repr__(self):
        return '<Task(%s)>' % self._alias

    def __str__(self):
        return self._alias

    def __cmp__(self, other):
        return cmp(self.progress, other.progress)

    @property
    def progress(self):
        """
        Returns/set the progress of this task.
        The progress is a value between 0.0 and 1.0, inclusively.
        """
        return self._progress

    @progress.setter
    def progress(self, value):
        with self._lock:
            if value < 0: value = 0.0
            if value > 1: value = 1.0
            self._progress = float(value)

    @property
    def status(self):
        """
        Returns/sets the status of this task.
        The status is a string.
        """
        return self._status

    @status.setter
    def status(self, text):
        with self._lock:
            if text is None: text = ''
            self._status = str(text)

_PROGRESS_GETTER = attrgetter('progress')

class ProgressTracker:

    def __init__(self):
        self._tasks = []
        self._lock = threading.RLock()

    def start_task(self, alias=None):
        """
        Starts a new task.
        
        :arg alias: alias of the task. If ``None``, the task is given a name based
            on its creation order.
        :type alias: :class:`str`
        """
        with self._lock:
            if not alias: alias = 'Task %i' % len(self._tasks)
            task = Task(alias)
            self._tasks.append(task)
            return task

    def stop_task(self, task):
        """
        Stops the specified task.
        If the stops was previously stopped, no exception is raised.
        A task cannot be started again after being stopped.
        """
        with self._lock:
            try:
                self._tasks.remove(task)
            except:
                pass

    def stop_all(self):
        """
        Stops all running tasks.
        """
        with self._lock:
            self._tasks = []

    def is_running(self):
        """
        Returns whether at least one task is alive.
        """
        with self._lock:
            return len(self._tasks) > 0

    def progress(self):
        """
        Returns the progress of all the tasks.
        The progress is a value between 0.0 and 1.0, inclusively.
        If more than one task is running, the average progress is returned.
        """
        with self._lock:
            if not self._tasks: return 0.0
            return sum(map(_PROGRESS_GETTER, self._tasks)) / len(self._tasks)

    def status(self):
        """
        Returns the status of the task with the highest progress.
        """
        with self._lock:
            if not self._tasks: return ''
            return sorted(self._tasks, reverse=True)[0].status

root = ProgressTracker()

def start_task(alias=None):
    """
    Starts a new task.
    
    :arg alias: alias of the task. If ``None``, the task is given a name based
        on its creation order.
    :type alias: :class:`str`
    """
    return root.start_task(alias)

def stop_task(task):
    """
    Stops the specified task.
    If the stops was previously stopped, no exception is raised.
    A task cannot be started again after being stopped.
    """
    root.stop_task(task)

def stop_all():
    """
    Stops all running tasks.
    """
    root.stop_all()

def is_running():
    """
    Returns whether at least one task is alive.
    """
    return root.is_running()

def progress():
    """
    Returns the progress of all the tasks.
    The progress is a value between 0.0 and 1.0, inclusively.
    If more than one task is running, the average progress is returned.
    """
    return root.progress()

def status():
    """
    Returns the status of the task with the highest progress.
    """
    return root.status()
