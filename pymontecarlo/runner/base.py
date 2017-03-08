"""
Base runner.
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.project import Project

# Globals and constants variables.

class Tracker(metaclass=abc.ABCMeta):

    def __init__(self, options):
        self.options = options

    @abc.abstractmethod
    def cancel(self):
        """
        Cancels the simulation
        """
        raise NotImplementedError

    @abc.abstractproperty
    def progress(self):
        """
        Returns progress of simulation as a :class:`float` from 0.0 to 1.0
        """
        return 0.0

    @abc.abstractproperty
    def status(self):
        """
        Returns status of simulation.
        """
        return ''

class Runner(metaclass=abc.ABCMeta):

    def __init__(self, project=None, max_workers=1):
        if project is None:
            project = Project()
        self.project = project

        self.max_workers = max_workers
        self.options_failed_count = 0
        self.options_cancelled_count = 0
        self.options_submitted_count = 0
        self.options_simulated_count = 0

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exctype, value, tb):
        self.shutdown(wait=True)
        return False

    @abc.abstractmethod
    def start(self):
        raise NotImplementedError

    @abc.abstractmethod
    def shutdown(self, wait=True):
        raise NotImplementedError

    def submit(self, options):
        """
        Submits the options in the queue and returns a :class:`Tracker` object.
        """
        program = options.program
        validator = program.create_validator()
        options = validator.validate_options(options)
        return self._submit(options)

    @abc.abstractmethod
    def _submit(self, options):
        """
        Actual implementation of :meth:`submit`.
        
        It should increment :var:`options_submitted_count` by one.
        
        :arg options: valid options
        """
        raise NotImplementedError

    @abc.abstractmethod
    def wait(self, timeout=None):
        raise NotImplementedError

    @property
    def progress(self):
        """
        Returns progress of runner as a :class:`float` from 0.0 to 1.0
        """
        return (self.options_simulated_count + \
                self.options_failed_count + \
                self.options_cancelled_count) / self.options_submitted_count
