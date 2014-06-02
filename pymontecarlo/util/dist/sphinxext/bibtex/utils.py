#!/usr/bin/env python
"""
================================================================================
:mod:`utils` -- Utilities for the extension
================================================================================

.. module:: utils
   :synopsis: Utilities for the extension

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os.path
import posixpath

# Third party modules.

# Local modules.

# Globals and constants variables.

def find_path(env, path):
    if path.startswith('/'):
        return posixpath.join(env.srcdir, path[1:])
    else:
        dirname = os.path.dirname(env.doc2path(env.docname))
        return posixpath.abspath(posixpath.join(dirname, path))

