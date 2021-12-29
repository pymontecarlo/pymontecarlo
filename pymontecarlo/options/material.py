"""
Material definition
"""

__all__ = ["Material", "MaterialBuilder", "VACUUM"]

# Standard library modules.
from operator import itemgetter
import itertools

# Third party modules.
import pyxray

import numpy as np

import matplotlib.colors

# Local modules.
from pymontecarlo.util.color import COLOR_SET_BROWN
from pymontecarlo.options.composition import (
    generate_name,
    from_formula,
    to_repr,
    calculate_density_kg_per_m3,
)
import pymontecarlo.options.base as base

# Globals and constants variables.


class LazyDensity(base.LazyOptionBase):
    def apply(self, material, options):
        composition = base.apply_lazy(material.composition, material, options)
        return calculate_density_kg_per_m3(composition)


class Material(base.OptionBase):

    WEIGHT_FRACTION_TOLERANCE = 1e-7  # 0.1 ppm
    DENSITY_TOLERANCE_kg_per_m3 = 1e-5

    COLOR_CYCLER = itertools.cycle(COLOR_SET_BROWN)

    def __init__(self, name, composition, density_kg_per_m3=None, color=None):
        """
        Creates a new material.

        :arg composition: composition in weight fraction.
            The composition is specified by a dictionary.
            The keys are atomic numbers and the values are weight fraction
            between ]0.0, 1.0].
        :type composition: :class:`dict`

        :arg name: name of the material
        :type name: :class:`str`

        :arg density_kg_per_m3: material's density in kg/m3. If ``None``, the
            density will be calculated by the validator.
        :type density_kg_per_m3: :class:`float`

        :arg color: color representing a material. If ``None``, a color is
            automatically selected from the provided color set. See
            :meth:`set_color_set`.
        """
        super().__init__()

        self.name = name
        self.composition = composition.copy()

        if density_kg_per_m3 is None:
            density_kg_per_m3 = LazyDensity()
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

        return cls(name, composition, density_kg_per_m3, color=color)

    @classmethod
    def from_formula(cls, formula, density_kg_per_m3=None, color=None):
        """
        Returns the material for the specified formula.

        :arg formula: formula of a molecule (e.g. ``Al2O3``)
        :type formula: :class:`str`
        """
        composition = from_formula(formula)
        return cls(formula, composition, density_kg_per_m3, color=color)

    def __repr__(self):
        return "<{classname}({name}, {composition}, {density:g} kg/m3)>".format(
            classname=self.__class__.__name__,
            name=self.name,
            composition=to_repr(self.composition),
            density=self.density_kg_per_m3,
        )

    def __str__(self):
        return self.name

    def __eq__(self, other):
        # NOTE: color is not tested in equality
        return (
            super().__eq__(other)
            and base.isclose(self.name, other.name)
            and base.are_mapping_value_close(
                self.composition,
                other.composition,
                abs_tol=self.WEIGHT_FRACTION_TOLERANCE,
            )
            and base.isclose(
                self.density_kg_per_m3,
                other.density_kg_per_m3,
                abs_tol=self.DENSITY_TOLERANCE_kg_per_m3,
            )
        )

    density_g_per_cm3 = base.MultiplierAttribute("density_kg_per_m3", 1e-3)

    # region HDF5

    ATTR_NAME = "name"
    DATASET_ATOMIC_NUMBER = "atomic number"
    DATASET_WEIGHT_FRACTION = "weight fraction"
    ATTR_DENSITY = "density (kg/m3)"
    ATTR_COLOR = "color"

    @classmethod
    def parse_hdf5(cls, group):
        name = cls._parse_hdf5(group, cls.ATTR_NAME, str)
        composition = cls._parse_hdf5_composition(group)
        density_kg_per_m3 = cls._parse_hdf5(group, cls.ATTR_DENSITY, float)
        color = cls._parse_hdf5(group, cls.ATTR_COLOR, str)
        return cls(name, composition, density_kg_per_m3, color)

    @classmethod
    def _parse_hdf5_composition(cls, group):
        zs = group[cls.DATASET_ATOMIC_NUMBER]
        wfs = group[cls.DATASET_WEIGHT_FRACTION]
        return dict((int(z), float(wf)) for z, wf in zip(zs, wfs))

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(group, self.ATTR_NAME, self.name)
        self._convert_hdf5_composition(group, self.composition)
        self._convert_hdf5(group, self.ATTR_DENSITY, self.density_kg_per_m3)
        self._convert_hdf5(group, self.ATTR_COLOR, matplotlib.colors.to_hex(self.color))

    def _convert_hdf5_composition(self, group, composition):
        zs = sorted(composition.keys())
        dataset_z = group.create_dataset(self.DATASET_ATOMIC_NUMBER, data=zs, dtype=int)

        wfs = [composition[z] for z in zs]
        dataset_wf = group.create_dataset(self.DATASET_WEIGHT_FRACTION, data=wfs)

        dataset_z.make_scale()
        dataset_wf.dims[0].label = self.DATASET_ATOMIC_NUMBER
        dataset_wf.dims[0].attach_scale(dataset_z)

    def convert_series(self, builder):
        super().convert_series(builder)

        for z, wf in self.composition.items():
            symbol = pyxray.element_symbol(z)
            name = "{} weight fraction".format(symbol)
            abbrev = "wt{}".format(symbol)
            tolerance = self.WEIGHT_FRACTION_TOLERANCE
            builder.add_column(name, abbrev, wf, tolerance=tolerance)

        builder.add_column(
            "density",
            "rho",
            self.density_kg_per_m3,
            "kg/m^3",
            self.DENSITY_TOLERANCE_kg_per_m3,
        )

        return builder

    # endregion

    # region Document

    TABLE_MATERIAL = "material"

    def convert_document(self, builder):
        super().convert_document(builder)

        table = builder.require_table(self.TABLE_MATERIAL)

        table.add_column("Name")
        table.add_column("Color")
        table.add_column("Density", "kg/m^3", self.DENSITY_TOLERANCE_kg_per_m3)
        for z in sorted(self.composition):
            name = pyxray.element_symbol(z)
            table.add_column(name, tolerance=self.WEIGHT_FRACTION_TOLERANCE)

        row = {
            "Name": self.name,
            "Color": matplotlib.colors.to_hex(self.color),
            "Density": self.density_kg_per_m3,
        }
        for z, wf in self.composition.items():
            symbol = pyxray.element_symbol(z)
            row[symbol] = wf
        table.add_row(row)


# endregion


class _Vacuum(Material):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            inst = Material.__new__(cls, *args, **kwargs)
            inst.name = "Vacuum"
            inst.composition = {}
            inst.density_kg_per_m3 = 0.0
            inst.color = "#00000000"  # invisible
            cls._instance = inst
        return cls._instance

    def __init__(self):
        pass

    def __repr__(self):
        return "<Vacuum()>"

    def __copy__(self):
        return VACUUM

    def __deepcopy__(self, memo):
        return VACUUM

    def __getstate__(self):
        return {}  # Nothing to pickle

    def __reduce__(self):
        return (self.__class__, ())

    @classmethod
    def parse_hdf5(cls, group):
        return VACUUM

    def convert_hdf5(self, group):
        base.OptionBase.convert_hdf5(self, group)

    def convert_series(self, builder):
        pass


VACUUM = _Vacuum()


class MaterialBuilder(base.OptionBuilderBase):
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
            density_kg_per_m3 = None

            material = Material(name, composition, density_kg_per_m3)
            materials.append(material)

        return materials
