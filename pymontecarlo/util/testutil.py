""""""

# Standard library modules.
import os
import pickle
import copy

# Third party modules.
import h5py

import pytest

# Local modules.

# Globals and constants variables.


def assert_copy(obj, assert_equality=True):
    obj2 = copy.copy(obj)
    if assert_equality:
        assert obj == obj2

    obj2 = copy.deepcopy(obj)
    if assert_equality:
        assert obj == obj2

    return obj2


def assert_pickle(obj, assert_equality=True):
    s = pickle.dumps(obj)
    obj2 = pickle.loads(s)
    if assert_equality:
        assert obj == obj2

    return obj2


def assert_convert_parse_hdf5(entity, tmp_path, assert_equality=True):
    filepath = os.path.join(tmp_path, "object.h5")

    with h5py.File(filepath, "w") as f:
        entity.convert_hdf5(f)

    with h5py.File(filepath, "r") as f:
        assert entity.can_parse_hdf5(f)
        entity2 = entity.parse_hdf5(f)

    if assert_equality:
        assert entity == entity2

    return entity2


def assert_ufloats(x, y, abs=1e-6):
    assert x.n == pytest.approx(y.n, abs=abs)
    assert x.s == pytest.approx(y.s, abs=abs)


def count_document_nodes(document):
    def recursive(node, total=0):
        if not hasattr(node, "children"):
            return total

        total += len(node.children)
        for childnode in node:
            return recursive(childnode, total)

        return total

    return recursive(document)
