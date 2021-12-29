""""""

# Standard library modules.

# Third party modules.
import pytest
import pandas as pd

# Local modules.
from pymontecarlo.formats.dataframe import ensure_distinct_columns

# Globals and constants variables.


@pytest.mark.parametrize(
    "df,tolerances,expected_columns",
    [
        (
            pd.DataFrame({"a": [1.001, 1.0, 1.01], "b": [2.0, 1.0, 3.0]}),
            {"a": 0.1, "b": 0.1},
            ("b",),
        ),
        (
            pd.DataFrame({"a": [1.001, 1.0, 1.01], "b": [2.0, 1.0, 3.0]}),
            {"a": 0.01, "b": 0.1},
            ("b",),
        ),
        (
            pd.DataFrame({"a": [1.001, 1.0, 1.01], "b": [2.0, 1.0, 3.0]}),
            {"a": 0.001, "b": 0.1},
            ("a", "b"),
        ),
        (
            pd.DataFrame({"a": [1.001, 1.0, 1.01], "b": [2.0, 1.0, 3.0]}),
            {"a": 10.0, "b": 10.0},
            (),
        ),
    ],
)
def test_ensure_distinct_columns(df, tolerances, expected_columns):
    newdf = ensure_distinct_columns(df, tolerances)
    assert tuple(newdf.columns) == expected_columns
