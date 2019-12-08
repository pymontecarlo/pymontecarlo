""""""

# Standard library modules.
import time
import threading
import enum
import logging

logger = logging.getLogger(__name__)

# Third party modules.
from tqdm.auto import tqdm

# Local modules.
from pymontecarlo.util.threadutil import RepeatTimer

# Globals and constants variables.


class TokenState(enum.IntEnum):
    """
    The states are ordered so that the maximum of a set of states indicates
    the overall state.
    """

    DONE = 0
    NOTSTARTED = 1
    CANCELLED = 2
    ERROR = 3
    RUNNING = 4


class Token:
    def __init__(self, name):
        self._name = name
        self._state = TokenState.NOTSTARTED
        self._progress = 0.0
        self._status = "Not started"
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

            logger.debug(
                'Token "{}" updated: progress={:.1f}%, status="{}", state={}'.format(
                    self._name, progress * 100, status, state.name
                )
            )

    def start(self, status=None):
        self.update(0.01, status or "Started", TokenState.RUNNING)

    def done(self, status=None):
        self.update(1.0, status or "Done", TokenState.DONE)

    def cancel(self, status=None):
        self.update(1.0, status or "Cancelled", TokenState.CANCELLED)

    def error(self, status=None):
        self.update(1.0, status or "Error", TokenState.ERROR)

    def reset(self):
        self._state = TokenState.NOTSTARTED
        self._progress = 0.0
        self._status = "Not started"
        self._latest_update = None
        self._subtokens.clear()

    def get_subtokens(self, category=None):
        with self._lock:
            if category is None:
                return tuple(self._subtokens)
            else:
                return tuple(
                    subtoken
                    for subtoken in self._subtokens
                    if subtoken._category == category
                )

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
            progresses = [
                subtoken.progress
                for subtoken in self._subtokens
                if subtoken._latest_update is not None
            ]

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
            statuses = [
                (subtoken._latest_update, subtoken.status)
                for subtoken in self._subtokens
                if subtoken._latest_update is not None
            ]

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
    NAME_MAX_LENGTH = 30

    def __init__(self, name):
        super().__init__(name)
        self._tqdm = None
        self._thread = None

    def _update_tqdm(self):
        if self._tqdm is None:
            return

        progress = int(self.progress * 100)
        self._tqdm.n = progress
        self._tqdm.refresh()

    def start(self, status=None):
        super().start(status)

        desc = (
            self._name
            if len(self._name) < self.NAME_MAX_LENGTH
            else self._name[: self.NAME_MAX_LENGTH] + "..."
        )
        leave = self._category is None
        self._tqdm = tqdm(total=100, desc=desc, leave=leave)

        self._thread = RepeatTimer(1, self._update_tqdm)
        self._thread.start()

    def done(self, status=None):
        super().done(status)

        if self._thread is not None:
            self._thread.cancel()
            self._thread.join()
            self._thread = None
            self._update_tqdm()

        if self._tqdm is not None:
            self._tqdm.close()
            self._tqdm = None
