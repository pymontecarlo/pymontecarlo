""""""

# Standard library modules.
import sys
import subprocess

# Third party modules.

# Local modules.
import psutil

# Globals and constants variables.


def create_startupinfo():
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    else:
        startupinfo = None

    return startupinfo


def kill_process(pid):
    psprocess = psutil.Process(pid)
    for subpsprocess in psprocess.children(recursive=True):
        subpsprocess.kill()
    psprocess.kill()
