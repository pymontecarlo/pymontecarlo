""""""

# Standard library modules.
import time
import threading
import enum
import logging
logger = logging.getLogger(__name__)

# Third party modules.
import tqdm

# Local modules.

# Globals and constants variables.

class TokenState(enum.IntEnum):
    """
    The states are ordered so that the maximum of a set of states indicates
    the overall state.
    """
    DONE = 0
    NOTSTARTED = 1
    RUNNING = 2
    CANCELLED = 3
    ERROR = 4

class Token:

    def __init__(self, name):
        self._name = name
        self._state = TokenState.NOTSTARTED
        self._progress = 0.0
        self._status = 'Not started'
        self._latest_update = None
        self._category = None
        self._lock = threading.Lock()
        self._subtokens = []

    def _create_subtoken(self, name, category):
        subtoken = self.__class__(name)
        subtoken._category = category
        return subtoken

    def create_subtoken(self, name, category=None):
        """
        Creates a new sub-token, with the specified name (thread-safe).
        """
        subtoken = self._create_subtoken(name, category)
        with self._lock:
            self._subtokens.append(subtoken)
        return subtoken

    def update(self, progress, status, state=None):
        """
        Updates the progress and status of this token (thread-safe).

        Args:
            progress (float): progress between 0.0 and 1.0
            status (str): status message
        """
        progress = max(0.0, min(1.0, progress))

        if state is None:
            state = TokenState.RUNNING

        with self._lock:
            self._state = state
            self._progress = progress
            self._status = status
            self._latest_update = time.monotonic()

            logger.debug('Token "{}" updated: progress={:.1f}%, status="{}", state={}'
                         .format(self._name, progress * 100, status, state.name))

    def start(self, status=None):
        self.update(0.01, status or 'Started', TokenState.RUNNING)

    def done(self, status=None):
        self.update(1.0, status or 'Done', TokenState.DONE)

    def cancel(self, status=None):
        self.update(1.0, status or 'Cancelled', TokenState.CANCELLED)

    def error(self, status=None):
        self.update(1.0, status or 'Error', TokenState.ERROR)

    def get_subtokens(self, category=None):
        with self._lock:
            if category is None:
                return tuple(self._subtokens)
            else:
                return tuple(subtoken for subtoken in self._subtokens if subtoken._category == category)

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        # Get state of all sub-tokens
        with self._lock:
            states = [subtoken.state for subtoken in self._subtokens]

        # Add state of current token, if it was updated
        if self._latest_update is not None:
            states.append(self._state)

        # Return highest state
        if not states:
            return TokenState.NOTSTARTED
        else:
            return max(states)

    @property
    def progress(self):
        """
        Returns the overall progress of this token and its sub-tokens.
        Only sub-tokens where the progress was updated are considered.
        """
        # Get progress of all sub-tokens, if it was updated
        with self._lock:
            progresses = [subtoken.progress for subtoken in self._subtokens
                          if subtoken._latest_update is not None]

        # Add progress of current token, if it was updated
        if self._latest_update is not None:
            progresses.append(self._progress)

        # Calculate total progress as the average of all progresses
        if not progresses:
            return 0.0
        else:
            return sum(progresses) / len(progresses)

    @property
    def status(self):
        """
        Returns the latest status of this token and its sub-tokens.
        """
        # Get status and latest update time of all sub-tokens, if it was updated
        with self._lock:
            statuses = [(subtoken._latest_update, subtoken.status)
                        for subtoken in self._subtokens
                        if subtoken._latest_update is not None]

        # Add status of current token, if it was updated
        if self._latest_update is not None:
            statuses.append((self._latest_update, self._status))

        # Return status of current token if no status exists
        # or the status of the latest updated sub-token.
        if not statuses:
            return self._status
        else:
            statuses.sort()
            return statuses[-1][1]

class TqdmToken(Token):

    def __init__(self, name, tqdm_class=None):
        super().__init__(name)

        if tqdm_class is None:
            tqdm_class = tqdm.tqdm
        self._tqdm_class = tqdm_class
        self._tqdm = None

    def _create_subtoken(self, name, category):
        """
        Creates a new sub-token, with the specified name (thread-safe).
        """
        subtoken = self.__class__(name, self._tqdm_class)
        subtoken._category = category
        return subtoken

    def update(self, progress, status, state=None):
        super().update(progress, status, state=state)

        if self._tqdm is None:
            self._tqdm = self._tqdm_class(total=100, desc=self.name)

        self._tqdm.n = int(self._progress * 100)
        self._tqdm.refresh()

        if self._progress == 1.0:
            self._tqdm.close()
            self._tqdm = None

