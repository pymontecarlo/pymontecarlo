#!/usr/bin/env python
"""
================================================================================
:mod:`build` -- Distribution builder
================================================================================

.. module:: build
   :synopsis: Distribution builder

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2010 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os

# Third party modules.

# Local modules.
from setuputilities.builder.project import Project
from setuputilities.builder.base import BaseBuild
from setuputilities.builder.setup import SetupBuild
from setuputilities.builder.doc import DocBuild
from setuputilities.builder.test import TestBuild
from setuputilities.builder.cover import CoverageBuild
from setuputilities.util import find_package_path, find_packages, find_package_data

# Globals and constants variables.

project = Project(find_package_path('sphinxtools.ext.bibtex'))

# Base Build
project.metadata.name = "bibtex"
project.metadata.version = "0.1"
project.metadata.author = "Philippe T. Pinard"
project.metadata.author_email = "philippe.pinard@gmail.com"
project.metadata.description = "Sphinx extension to use BibTeX references"
project.metadata.license = "GPL v3"
project.metadata.classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development"]
project.metadata.platforms = "OS Independent"

# Setup Build
project.packages = find_packages("sphinxtools.ext.bibtex", where=project.dir)
project.package_data = \
    find_package_data(package='sphinxtools.ext.bibtex', where=project.dir)
project.data_files = []

# Doc Build
project.doc_dir = os.path.join(project.dir, 'doc')

class Build(BaseBuild, SetupBuild, DocBuild, TestBuild, CoverageBuild):

    def __init__(self, project):
        BaseBuild.__init__(self, project)
        SetupBuild.__init__(self, project)
        DocBuild.__init__(self, project)
        TestBuild.__init__(self, project)
        CoverageBuild.__init__(self, project)

if __name__ == '__main__': #pragma: no cover
    build = Build(project)
    build.run()
