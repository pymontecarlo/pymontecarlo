#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import pickle

# Third party modules.

# Local modules.
from pymontecarlo.options.model.base import ModelBase

# Globals and constants variables.

class ModelMock(ModelBase):

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

    def testpickle(self):
        s = pickle.dumps(ModelMock.A)
        model = pickle.loads(s)
        self.assertEqual(ModelMock.A, model)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
