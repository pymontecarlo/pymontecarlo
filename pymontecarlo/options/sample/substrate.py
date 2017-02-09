"""
Substrate sample.
"""

# Standard library modules.
import functools
import itertools
import operator

# Third party modules.

# Local modules.
from pymontecarlo.options.sample.base import Sample, SampleBuilder

# Globals and constants variables.

class SubstrateSample(Sample):

    NAME = 'substrate sample'
    DESCRIPTION = 'Describes an infinitely thick sample.'

    def __init__(self, material, tilt_rad=0.0, rotation_rad=0.0):
        """
        Creates a substrate sample. 
        At tilt of 0.0\u00b0, the sample is entirely made of the specified 
        material below ``z = 0``.
        """
        super().__init__(tilt_rad, rotation_rad)
        self.material = material

    def __repr__(self):
        return '<{0:s}(material={1:s})>' \
            .format(self.__class__.__name__, self.material)

    def __eq__(self, other):
        return super().__eq__(other) and self.material == other.material

    def create_datarow(self):
        datarow = super().create_datarow()
        for name, value in self.material.create_datarow().items():
            datarow["substrate's " + name] = value
        return datarow

    @property
    def materials(self):
        return self._cleanup_materials(self.material)

class SubstrateSampleBuilder(SampleBuilder):

    def __init__(self):
        super().__init__()
        self.materials = []

    def __len__(self):
        it = [super().__len__(), len(self.materials)]
        return functools.reduce(operator.mul, it)

    def add_material(self, material):
        if material not in self.materials:
            self.materials.append(material)

    def build(self):
        product = itertools.product(self.materials, *self._get_combinations())
        return [SubstrateSample(*args) for args in product]
