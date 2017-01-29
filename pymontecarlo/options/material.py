"""
Material definition
"""

__all__ = ['Material',
           'VACUUM',
           'MaterialBuilder']

# Standard library modules.
from operator import itemgetter
import itertools

# Third party modules.
import pyxray

import numpy as np

# Local modules.
from pymontecarlo.util.cbook import MultiplierAttribute, Builder
from pymontecarlo.util.composition import calculate_density_kg_per_m3, generate_name

# Globals and constants variables.

class Material(object):

    def __init__(self, name, composition, density_kg_per_m3):
        """
        Creates a new material.

        :arg composition: composition in weight fraction.
            The composition is specified by a dictionary.
            The keys are atomic numbers and the values are weight fraction 
            between ]0.0, 1.0].
        :type composition: :class:`dict`

        :arg name: name of the material
        :type name: :class:`str`

        :arg density_kg_per_m3: material's density in kg/m3.
        :type density_kg_per_m3: :class:`float`
        """
        self.name = name
        self.composition = composition.copy()
        self.density_kg_per_m3 = density_kg_per_m3

    @classmethod
    def pure(cls, z):
        """
        Returns the material for the specified pure element.

        :arg z: atomic number
        :type z: :class:`int`
        """
        name = pyxray.element_name(z)
        composition = {z: 1.0}
        density_kg_per_m3 = pyxray.element_mass_density_kg_per_m3(z)

        return cls(name, composition, density_kg_per_m3)

    @classmethod
    def from_formula(cls, formula, density_kg_per_m3=None):
        """
        Returns the material for the specified formula.
        
        :arg formula: formula of a molecule (e.g. ``Al2O3``)
        :type formula: :class:`str`
        """
        composition = cls._composition_from_formula(formula)
        return cls(composition, formula, density_kg_per_m3)

    def __repr__(self):
        return '<Material(name=%s, composition=%s, density=%s kg/m3)>' % \
            (self.name, self.composition, self.density_kg_per_m3)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name and \
            self.composition == other.composition and \
            self.density_kg_per_m3 == other.density_kg_per_m3

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((self.__class__,
                     self.name,
                     tuple(sorted(self.composition.items(), key=itemgetter(0))),
                     self.density_kg_per_m3))

    density_g_per_cm3 = MultiplierAttribute('density_kg_per_m3', 1e-3)

class _Vacuum(Material):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            inst = Material.__new__(cls, *args, **kwargs)
            inst.name = 'Vacuum'
            inst.composition = {}
            inst.density_kg_per_m3 = 0.0
            cls._instance = inst
        return cls._instance

    def __init__(self):
        pass

    def __repr__(self):
        return '<Vacuum()>'

    def __copy__(self):
        return VACUUM

    def __deepcopy__(self, memo):
        return VACUUM

    def __getstate__(self):
        return {} # Nothing to pickle

    def __reduce__(self):
        return (self.__class__, ())

VACUUM = _Vacuum()

class MaterialBuilder(Builder):

    def __init__(self, balance_z):
        self.balance_z = balance_z
        self.elements = {}

    def add_element(self, z, *wf):
        self.elements[z] = np.ravel(wf)
        return self

    def add_element_range(self, z, wf0, wf1, wfstep):
        self.elements[z] = np.arange(wf0, wf1, wfstep)
        return self

    def add_element_interval(self, z, wf0, wf1, nstep):
        self.elements[z] = np.linspace(wf0, wf1, nstep, endpoint=True)
        return self

    def build(self):
        combinations = []
        for z, wfs in self.elements.items():
            combination = []
            for wf in wfs:
                combination.append((z, wf))
            combinations.append(combination)

        materials = []
        for combination in itertools.product(*combinations):
            composition = dict(combination)

            total = sum(map(itemgetter(1), combination))
            remainder = 1.0 - total
            composition[self.balance_z] = remainder

            name = generate_name(composition)
            density_kg_per_m3 = calculate_density_kg_per_m3(composition)

            material = Material(name, composition, density_kg_per_m3)
            materials.append(material)

        return materials

