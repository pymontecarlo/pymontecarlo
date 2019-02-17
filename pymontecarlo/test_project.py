#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.results.photonintensity import \
    EmittedPhotonIntensityResult, GeneratedPhotonIntensityResult
import pymontecarlo.util.testutil as testutil

# Globals and constants variables.

def test_project(project):
    assert len(project.simulations) == 3
    assert len(project.result_classes) == 3

def test_project_hdf5(project, tmp_path):
    project2 = testutil.assert_convert_parse_hdf5(project, tmp_path, assert_equality=False)
    assert len(project2.simulations) == 3
    assert len(project2.result_classes) == 3

def test_project_copy(project):
    project2 = testutil.assert_copy(project, assert_equality=False)
    assert len(project2.simulations) == 3
    assert len(project2.result_classes) == 3

def test_project_pickle(project):
    project2 = testutil.assert_pickle(project, assert_equality=False)
    assert len(project2.simulations) == 3
    assert len(project2.result_classes) == 3

def test_project_create_options_dataframe(project, settings):
    df = project.create_options_dataframe(settings, only_different_columns=False)
    assert len(df) == 3

def test_project_create_options_dataframe_only_different_columns(project, settings):
    df = project.create_options_dataframe(settings, only_different_columns=True)
    assert len(df) == 3

    assert len(df.loc[0]) == 4
    assert len(df.loc[1]) == 4
    assert len(df.loc[2]) == 4

def test_project_create_results_dataframe(project, settings):
    df = project.create_results_dataframe(settings)
    assert len(df) == 3

    assert len(df.loc[0]) == 34
    assert len(df.loc[1]) == 34
    assert len(df.loc[2]) == 34

    assert len(df.loc[0].dropna()) == 28
    assert len(df.loc[1].dropna()) == 28
    assert len(df.loc[2].dropna()) == 34

def test_project_create_results_dataframe_with_results(project, settings):
    result_classes = [EmittedPhotonIntensityResult]
    df = project.create_results_dataframe(settings, result_classes)
    assert len(df) == 3

    assert len(df.loc[0]) == 14
    assert len(df.loc[1]) == 14
    assert len(df.loc[2]) == 14

def test_project_create_results_dataframe_with_missing_results(project, settings):
    result_classes = [GeneratedPhotonIntensityResult]
    df = project.create_results_dataframe(settings, result_classes)
    assert len(df) == 3

    assert len(df.loc[0]) == 6
    assert len(df.loc[1]) == 6
    assert len(df.loc[2]) == 6

    assert len(df.loc[0].dropna()) == 0
    assert len(df.loc[1].dropna()) == 0
    assert len(df.loc[2].dropna()) == 6

def test_project_create_results_dataframe_with_two_results(project, settings):
    result_classes = [EmittedPhotonIntensityResult, GeneratedPhotonIntensityResult]
    df = project.create_results_dataframe(settings, result_classes)
    assert len(df) == 3

    assert len(df.loc[0]) == 20
    assert len(df.loc[1]) == 20
    assert len(df.loc[2]) == 20

    assert len(df.loc[0].dropna()) == 14
    assert len(df.loc[1].dropna()) == 14
    assert len(df.loc[2].dropna()) == 20

#def testread_write(self):
#    filepath = os.path.join(self.create_temp_dir(), 'project.h5')
#    self.p.write(filepath)
#    p = Project.read(filepath)
#    self.assertEqual(3, len(p.simulations))
#    self.assertEqual(3, len(p.result_classes))
