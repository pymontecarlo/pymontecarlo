#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.options.model.base import Model

# Globals and constants variables.

class ModelMock(Model):

    A = ('model A', 'doe2017')
    B = ('model B', 'adams1990')

class TestModel(unittest.TestCase):

    def testskeleton(self):
        self.assertEqual('model A', ModelMock.A.fullname)
        self.assertEqual('doe2017', ModelMock.A.reference)

        self.assertEqual('model B', ModelMock.B.fullname)
        self.assertEqual('adams1990', ModelMock.B.reference)

    def test__str__(self):
        self.assertEqual('model A', str(ModelMock.A))
        self.assertEqual('model B', str(ModelMock.B))

    def test__eq__(self):
        self.assertTrue(ModelMock.A == ModelMock.A)
        self.assertTrue(ModelMock.A != ModelMock.B)

    def test__in__(self):
        self.assertIn(ModelMock.A, [ModelMock.A, ModelMock.B])

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
