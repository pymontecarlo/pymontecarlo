#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.model.base import ModelBase
from pymontecarlo.options.base import OptionBase
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.

class ModelMock(ModelBase):

    A = ('model A', 'doe2017')
    B = ('model B', 'adams1990')

class OptionMock(OptionBase):

    ATTR_MODEL = 'model'

    def __init__(self, model):
        self.model = model

    def __eq__(self, other):
        return super().__eq__(other) and self.model == other.model

    @classmethod
    def parse_hdf5(cls, group):
        model = cls._parse_hdf5(group, cls.ATTR_MODEL, ModelMock)
        return cls(model)

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(group, self.ATTR_MODEL, self.model)

def test_model():
    assert ModelMock.A.fullname == 'model A'
    assert ModelMock.A.reference == 'doe2017'

    assert ModelMock.B.fullname == 'model B'
    assert ModelMock.B.reference == 'adams1990'

def test_model_str():
    assert str(ModelMock.A) == 'model A'
    assert str(ModelMock.B) == 'model B'

def test_model_eq():
    assert ModelMock.A == ModelMock.A
    assert ModelMock.A != ModelMock.B

def test_model_in():
    assert ModelMock.A in [ModelMock.A, ModelMock.B]

def test_model_hdf5(tmp_path):
    option = OptionMock(ModelMock.A)
    testutil.assert_convert_parse_hdf5(option, tmp_path)

def test_model_copy():
    testutil.assert_copy(ModelMock.A)

def test_model_pickle():
    testutil.assert_pickle(ModelMock.A)
