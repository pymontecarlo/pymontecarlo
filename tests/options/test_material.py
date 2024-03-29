#!/usr/bin/env python
""" """

# Standard library modules.
import copy
import pickle
import itertools

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.options.material import Material, VACUUM, MaterialBuilder
import pymontecarlo.options.base as base
from pymontecarlo.options.parameter import ParameterType
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.


@pytest.fixture
def material():
    return Material("Pure Cu", {29: 1.0}, 8960.0, "#FF0000")


@pytest.fixture
def lazy_material():
    return Material("test", {29: 1.0})


@pytest.fixture
def builder():
    builder = MaterialBuilder(26)
    builder.add_element(29, 0.05)
    builder.add_element_range(28, 0.1, 0.2, 0.02)
    builder.add_element(24, (0.01, 0.05, 0.07))
    builder.add_element_interval(6, 0.0, 1.0, 5)
    return builder


def test_material(material):
    assert str(material) == "Pure Cu"
    assert material.name == "Pure Cu"

    assert 29 in material.composition
    assert material.composition[29] == pytest.approx(1.0, abs=1e-9)

    assert material.density_kg_per_m3 == pytest.approx(8960.0, abs=1e-4)
    assert material.density_g_per_cm3 == pytest.approx(8.960, abs=1e-4)

    assert material.color == "#FF0000"


def test_material_repr(material):
    assert repr(material) == "<Material(Pure Cu, 100%Cu, 8960 kg/m3)>"


def test_material_eq(material):
    assert material == Material("Pure Cu", {29: 1.0}, 8960.0)

    assert not material == Material("Pure Cu", {29: 1.0}, 8961.0)
    assert not material == Material("Pure Cu", {29: 0.5, 30: 0.5}, 8960.0)


def test_material_getparameters_pure(material):
    assert len(material.get_parameters(lambda options: material)) == 0


def test_material_getparameters_compound():
    material = Material.from_formula("CaSiO3")
    parameters = material.get_parameters(lambda options: material)

    assert len(parameters) == 3
    assert parameters[0].get_value(None) == pytest.approx(
        material.composition[20], abs=1e-6
    )
    assert parameters[1].get_value(None) == pytest.approx(
        material.composition[14], abs=1e-6
    )
    assert parameters[2].get_value(None) == pytest.approx(
        material.composition[8], abs=1e-6
    )

    parameters[0].type_ = ParameterType.UNKNOWN
    parameters[0].set_value(None, 0.5)
    assert parameters[0].get_value(None) == pytest.approx(0.5, abs=1e-6)
    assert material.composition[20] == pytest.approx(0.5, abs=1e-6)


@pytest.mark.parametrize(
    "parameter_types,expected_composition",
    [
        (
            [ParameterType.UNKNOWN, ParameterType.FIXED, ParameterType.DIFFERENCE],
            {22: 0.5, 24: 0.2, 29: 0.3},
        ),
        (
            [ParameterType.UNKNOWN, ParameterType.DIFFERENCE, ParameterType.DIFFERENCE],
            {22: 0.5, 24: 0.25, 29: 0.25},
        ),
        (
            [ParameterType.UNKNOWN, ParameterType.UNKNOWN, ParameterType.DIFFERENCE],
            {22: 0.5, 24: 0.2, 29: 0.3},
        ),
    ],
)
def test_material_getparameters_parametertype(parameter_types, expected_composition):
    material = Material("TiCrCu", {22: 0.2, 24: 0.2, 29: 0.6})
    parameters = material.get_parameters(lambda options: material)

    # Set parameter types
    for parameter, parameter_type in zip(parameters, parameter_types):
        parameter.type_ = parameter_type

    # Set titanium concentration
    parameters[0].set_value(None, 0.5)

    # Test
    for z, expected_wf in expected_composition.items():
        assert material.composition[z] == pytest.approx(expected_wf, abs=1e-6)


@pytest.mark.parametrize(
    "parameter_types,error_count",
    [
        (
            [ParameterType.FIXED] * 3,
            0,
        ),
        (
            [ParameterType.FIXED, ParameterType.FIXED, ParameterType.UNKNOWN],
            1,
        ),
        (
            [ParameterType.FIXED, ParameterType.FIXED, ParameterType.DIFFERENCE],
            1,
        ),
        (
            [ParameterType.FIXED, ParameterType.UNKNOWN, ParameterType.FIXED],
            1,
        ),
        (
            [ParameterType.FIXED, ParameterType.UNKNOWN, ParameterType.UNKNOWN],
            1,
        ),
        (
            [ParameterType.FIXED, ParameterType.UNKNOWN, ParameterType.DIFFERENCE],
            0,
        ),
        (
            [ParameterType.FIXED, ParameterType.DIFFERENCE, ParameterType.FIXED],
            1,
        ),
        (
            [ParameterType.FIXED, ParameterType.DIFFERENCE, ParameterType.UNKNOWN],
            0,
        ),
        (
            [ParameterType.FIXED, ParameterType.DIFFERENCE, ParameterType.DIFFERENCE],
            1,
        ),
    ],
)
def test_material_getparameters_validate(parameter_types, error_count):
    material = Material("TiCrCu", {22: 0.2, 24: 0.2, 29: 0.6})
    parameters = material.get_parameters(lambda options: material)

    # Set parameter types
    for parameter, parameter_type in zip(parameters, parameter_types):
        parameter.type_ = parameter_type

    errors = parameters[0].validate(None)
    assert len(errors) == error_count


def test_material_hdf5(material, tmp_path):
    testutil.assert_convert_parse_hdf5(material, tmp_path)


def test_material_copy(material):
    testutil.assert_copy(material)


def test_material_pickle(material):
    testutil.assert_pickle(material)


def test_material_series(material, seriesbuilder):
    material.convert_series(seriesbuilder)
    assert len(seriesbuilder.build()) == 2


def test_material_document(material, documentbuilder):
    material.convert_document(documentbuilder)
    document = documentbuilder.build()
    assert testutil.count_document_nodes(document) == 9


def test_material_pure():
    material = Material.pure(29)

    assert str(material) == "Copper"
    assert material.name == "Copper"

    assert 29 in material.composition
    assert material.composition[29] == pytest.approx(1.0, abs=1e-9)

    assert material.density_kg_per_m3 == pytest.approx(8960.0, abs=1e-4)
    assert material.density_g_per_cm3 == pytest.approx(8.960, abs=1e-4)


def test_material_from_formula():
    material = Material.from_formula("SiO2", 1250.0)

    assert str(material) == "SiO2"
    assert material.name == "SiO2"

    assert 14 in material.composition
    assert material.composition[14] == pytest.approx(0.4674, abs=1e-4)

    assert 8 in material.composition
    assert material.composition[8] == pytest.approx(0.5326, abs=1e-4)

    assert material.density_kg_per_m3 == pytest.approx(1250.0, abs=1e-4)
    assert material.density_g_per_cm3 == pytest.approx(1.25, abs=1e-4)


def test_material_setcolorset():
    Material.set_color_set(["#00FF00", "#0000FF"])

    assert Material.pure(13).color == "#00FF00"
    assert Material.pure(14).color == "#0000FF"
    assert Material.pure(15).color == "#00FF00"


def test_lazymaterial(material, lazy_material):
    assert lazy_material == lazy_material
    assert material != lazy_material

    density_kg_per_m3 = base.apply_lazy(
        lazy_material.density_kg_per_m3, lazy_material, None
    )
    assert density_kg_per_m3 == pytest.approx(8960.0, abs=1e-4)

    density_g_per_cm3 = base.apply_lazy(
        lazy_material.density_g_per_cm3, lazy_material, None
    )
    assert density_g_per_cm3 == pytest.approx(8.9600, abs=1e-4)


def test_lazymaterial_hdf5(lazy_material, tmp_path):
    testutil.assert_convert_parse_hdf5(lazy_material, tmp_path)


def test_lazymaterial_copy(lazy_material):
    testutil.assert_copy(lazy_material)


def test_lazymaterial_pickle(lazy_material):
    testutil.assert_pickle(lazy_material)


def test_lazymaterial_series(lazy_material, seriesbuilder):
    lazy_material.convert_series(seriesbuilder)
    assert len(seriesbuilder.build()) == 2


def test_lazymaterial_document(lazy_material, documentbuilder):
    lazy_material.convert_document(documentbuilder)
    document = documentbuilder.build()
    assert testutil.count_document_nodes(document) == 9


def test_vacuum():
    assert str(VACUUM) == "Vacuum"
    assert VACUUM.composition == {}
    assert VACUUM.density_kg_per_m3 == pytest.approx(0.0, abs=1e-4)
    assert VACUUM.color == "#00000000"


def test_vacuum_copy():
    assert copy.copy(VACUUM) is VACUUM
    assert copy.deepcopy(VACUUM) is VACUUM


def test_vacuum_pickle():
    assert pickle.loads(pickle.dumps(VACUUM)) is VACUUM


def test_vacuum_repr():
    assert repr(VACUUM) == "<Vacuum()>"


def test_materialbuilder(builder):
    assert len(builder) == 5 * 3 * 5
    assert len(builder.build()) == 5 * 3 * 5


def test_materialbuilder_noelement():
    builder = MaterialBuilder(26)
    assert len(builder) == 1
    assert len(builder.build()) == 1
