#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.hdf5.project import ProjectHDF5Handler

# Globals and constants variables.

class TestProjectHDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = ProjectHDF5Handler()
        project = self.create_basic_project()
        project2 = self.convert_parse_hdf5handler(handler, project)

        self.assertEqual(len(project.simulations), len(project2.simulations))

#        import h5py
#        with h5py.File('/tmp/project.h5', 'w') as f:
#            handler.convert(project, f)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
