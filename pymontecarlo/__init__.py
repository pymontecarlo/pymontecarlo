"""
Common interface to several Monte Carlo codes
"""

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

# Standard library modules.
import os
import sys
import logging
logger = logging.getLogger(__name__)
import threading

# Third party modules.

# Local modules.

# Globals and constants variables.

def _get_home():
    """
    .. note:: From matplotlib
    
    Find user's home directory if possible.
    Otherwise, returns None.

    :see:
        http://mail.python.org/pipermail/python-list/2005-February/325395.html
    """
    try:
        path = os.path.expanduser("~")
    except ImportError:
        # This happens on Google App Engine (pwd module is not present).
        pass
    else:
        if os.path.isdir(path):
            return path
    for evar in ('HOME', 'USERPROFILE', 'TMP'):
        path = os.environ.get(evar)
        if path is not None and os.path.isdir(path):
            return path
    return None

def _get_xdg_config_dir():
    """
    .. note:: From matplotlib
    
    Returns the XDG configuration directory, according to the `XDG
    base directory spec
    <http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html>`_.
    """
    path = os.environ.get('XDG_CONFIG_HOME')
    if path is None:
        path = _get_home()
        if path is not None:
            path = os.path.join(path, '.config')
    return path

def _get_config_dir():
    configdir = os.environ.get('PYMONTECARLO_CONFIGDIR')
    if configdir is not None:
        configdir = os.path.abspath(configdir)

    else:
        h = _get_home()
        if h is not None:
            configdir = os.path.join(h, '.pymontecarlo')

        if sys.platform.startswith('linux'):
            xdg_base = _get_xdg_config_dir()
            if xdg_base is not None:
                configdir = os.path.join(xdg_base, 'pymontecarlo')

    if configdir is None:
        raise IOError('Could not find config dir')

    os.makedirs(configdir, exist_ok=True)
    return configdir

#--- Units

import pint

unit_registry = pint.UnitRegistry()
unit_registry.define('electron = mol')

#--- HDF5 handlers

from pkg_resources import iter_entry_points

_HDF5HANDLER_ENTRYPOINT = 'pymontecarlo.fileformat'
_hdf5handlers = None

def _load_hdf5handlers():
    global _hdf5handlers

    # NOTE: This is an important check. If the entry points are resolved in
    # another thread than the main one, the import hangs
    if threading.current_thread() != threading.main_thread():
        raise RuntimeError('Handler must be initialized in main thread')

    _hdf5handlers = tuple(ep.resolve()() for ep in iter_entry_points(_HDF5HANDLER_ENTRYPOINT))
    logging.debug('Initialized handlers: ' + str(_hdf5handlers))

def reload_hdf5handlers():
    global _hdf5handlers
    _hdf5handlers = None
    return _load_hdf5handlers()

def iter_hdf5handlers():
    global _hdf5handlers
    if _hdf5handlers is None:
        _load_hdf5handlers()
    return iter(_hdf5handlers)

#--- Settings

from pymontecarlo.fileformat.reader import HDF5ReaderMixin
from pymontecarlo.fileformat.writer import HDF5WriterMixin

class Settings(HDF5ReaderMixin, HDF5WriterMixin):

    def __init__(self, programs=None):
        if programs is None:
            programs = []
        self.programs = tuple(programs)

        # Units
        self.preferred_units = {}

        # X-ray line
        self.preferred_xrayline_notation = 'iupac'
        self.preferred_xrayline_encoding = 'utf16'

    def set_preferred_unit(self, unit):
        if isinstance(unit, str):
            unit = unit_registry.parse_units(unit)

        _, base_unit = unit_registry._get_base_units(unit)
        self.preferred_units[base_unit] = unit

    def clear_preferred_units(self):
        self.preferred_units.clear()

    def to_preferred_unit(self, q):
        _, base_unit = unit_registry._get_base_units(q.units)

        try:
            preferred_unit = self.preferred_units[base_unit]
            return q.to(preferred_unit)
        except KeyError:
            return q.to(base_unit)

settings = None

def _load_settings(filepath=None):
    global settings

    if filepath is None:
        filepath = os.path.join(_get_config_dir(), 'settings.h5')

    try:
        settings = Settings.read(filepath)
    except:
        logger.exception('load settings')
        settings = Settings()

def reload_settings():
    _load_settings()

def _init():
    _load_hdf5handlers()
    _load_settings()

_init()
