"""
Material definition
"""

# Standard library modules.
import math
from operator import itemgetter
import itertools

# Third party modules.
import pyxray

import numpy as np

# Local modules.
import pymontecarlo.util.cbook as cbook
from pymontecarlo.util.color import COLOR_SET_BROWN
from pymontecarlo.options.composition import \
    calculate_density_kg_per_m3, generate_name, from_formula
from pymontecarlo.options.base import Option, OptionBuilder

# Globals and constants variables.

class Material(Option):

    WEIGHT_FRACTION_TOLERANCE = 1e-7 # 0.1 ppm
    DENSITY_TOLERANCE_kg_per_m3 = 1e-5

    COLOR_CYCLER = itertools.cycle(COLOR_SET_BROWN)

    def __init__(self, name, composition, density_kg_per_m3, color=None):
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
        
        :arg color: color representing a material. If ``None``, a color is
            automatically selected from the provided color set. See
            :meth:`set_color_set`.
        """
        super().__init__()

        self.name = name
        self.composition = composition.copy()
        self.density_kg_per_m3 = density_kg_per_m3

        if color is None:
            color = next(self.COLOR_CYCLER)
        self.color = color

    @classmethod
    def set_color_set(cls, color_set):
        """
        Sets the set of colors used to assign a color to a material.
        
        :arg color_set: iterable of colors
        """
        cls.COLOR_CYCLER = itertools.cycle(color_set)

    @classmethod
    def pure(cls, z, color=None):
        """
        Returns the material for the specified pure element.

        :arg z: atomic number
        :type z: :class:`int`
        """
        name = pyxray.element_name(z)
        composition = {z: 1.0}
        density_kg_per_m3 = pyxray.element_mass_density_kg_per_m3(z)

        return cls(name, composition, density_kg_per_m3, color)

    @classmethod
    def from_formula(cls, formula, density_kg_per_m3=None, color=None):
        """
        Returns the material for the specified formula.
        
        :arg formula: formula of a molecule (e.g. ``Al2O3``)
        :type formula: :class:`str`
        """
        composition = from_formula(formula)

        if density_kg_per_m3 is None:
            density_kg_per_m3 = calculate_density_kg_per_m3(composition)

        return cls(formula, composition, density_kg_per_m3, color)

    def __repr__(self):
        return '<{classname}({name}, {composition}, {density:g} kg/m3)>' \
            .format(classname=self.__class__.__name__,
                    name=self.name,
                    composition=' '.join('{1:g}%{0}'.format(pyxray.element_symbol(z), wf * 100.0)
                                         for z, wf in self.composition.items()),
                    density=self.density_kg_per_m3)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        # NOTE: color is not tested in equality
        return super().__eq__(other) and \
            self.name == other.name and \
            cbook.are_mapping_value_close(self.composition, other.composition, abs_tol=self.WEIGHT_FRACTION_TOLERANCE) and \
            math.isclose(self.density_kg_per_m3, other.density_kg_per_m3, abs_tol=self.DENSITY_TOLERANCE_kg_per_m3)

    density_g_per_cm3 = cbook.MultiplierAttribute('density_kg_per_m3', 1e-3)

class _Vacuum(Material):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            inst = Material.__new__(cls, *args, **kwargs)
            inst.name = 'Vacuum'
            inst.composition = {}
            inst.density_kg_per_m3 = 0.0
            inst.color = (0.0, 0.0, 0.0, 0.0) # invisible
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

class MaterialBuilder(OptionBuilder):

    def __init__(self, balance_z):
        self.balance_z = balance_z
        self.elements = {}

    def __len__(self):
        count = 1
        for wfs in self.elements.values():
            count *= len(wfs)
        return count

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

