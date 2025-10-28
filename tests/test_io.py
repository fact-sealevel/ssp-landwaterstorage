import numpy as np

from ssp_landwaterstorage.core import (
    ReservoirImpoundment,
    Locations,
    PopulationHistory,
    GroundwaterDepletion,
    PopulationScenarios,
)
from ssp_landwaterstorage.io import (
    read_reservoir_impoundment,
    read_locations,
    read_population_history,
    read_groundwater_depletion,
    read_population_scenarios,
)


def test_read_reservoir_impoundment_file(tmp_path):
    """
    Test can instantiate ReservoirImpoundment from CSV.
    """
    tmpfl = tmp_path / "impoundment.csv"
    tmpfl.write_text("year,mm\n1918.847,0.212\n1921.394,0.212\n")

    actual = read_reservoir_impoundment(tmpfl)

    expected = ReservoirImpoundment(
        t=np.array([1918.847, 1921.394]), impoundment=np.array([0.212, 0.212])
    )

    np.testing.assert_allclose(actual.t, expected.t)
    np.testing.assert_allclose(actual.impoundment, expected.impoundment)


def test_read_reservoir_impoundment_file_windows_line_ending(tmp_path):
    """
    Test can instantiate ReservoirImpoundment from CSV with Windows line endings.
    """
    tmpfl = tmp_path / "impoundment_windows.csv"
    tmpfl.write_text("year,mm\r\n1918.847,0.212\r\n")

    actual = read_reservoir_impoundment(tmpfl)

    expected = ReservoirImpoundment(
        t=np.array([1918.847]), impoundment=np.array([0.212])
    )

    np.testing.assert_allclose(actual.t, expected.t)
    np.testing.assert_allclose(actual.impoundment, expected.impoundment)


def test_read_locations(tmp_path):
    """
    Test can get Locations from a locations.lst (tab-delimited?) file.
    """
    tmpfl = tmp_path / "location.lst"
    tmpfl.write_text("New_York\t12\t40.70\t-74.01")

    actual = read_locations(tmpfl)

    expected = Locations(
        name=np.array(["New_York"]),
        id=np.array([12]),
        lat=np.array([40.70]),
        lon=np.array([-74.01]),
    )

    assert actual.name == expected.name
    assert actual.id == expected.id
    np.testing.assert_allclose(actual.lat, expected.lat)
    np.testing.assert_allclose(actual.lon, expected.lon)


def test_read_population_history(tmp_path):
    """
    Test can instantiate PopulationHistory from CSV.
    """
    tmpfl = tmp_path / "population_history.csv"
    tmpfl.write_text("year,pop\n1950,0\n1951,1\n1952,2\n1953,3\n1954,4\n1955,5\n1956,6")

    actual = read_population_history(tmpfl)

    expected = PopulationHistory(
        t=np.array([1950, 1955]),
        pop=np.array([0, 5]),
        t0=np.array([1950, 1951, 1952, 1953, 1954, 1955, 1956]),
        pop0=np.array([0, 1, 2, 3, 4, 5, 6]),
    )

    np.testing.assert_allclose(actual.t, expected.t)
    np.testing.assert_allclose(actual.pop, expected.pop)
    np.testing.assert_allclose(actual.t0, expected.t0)
    np.testing.assert_allclose(actual.pop0, expected.pop0)


def test_read_groundwater_depletion(tmp_path):
    """
    Test can get GroundwaterDepletion from a single CSV.
    """
    tmpfl = tmp_path / "gwd.csv"
    # For some reason, one of the original gwd files had duplicate entries so here we do it too.
    tmpfl.write_text(
        "year,mm\n1941.902,0.396\n1941.902,0.396\n1942.542,0.396\n1942.542,0.396"
    )

    actual = read_groundwater_depletion([tmpfl])

    expected = GroundwaterDepletion(
        t=np.array([[1941.902, 1941.902, 1942.542, 1942.542, np.nan]]),
        depletion=np.array([[0.396, 0.396, 0.396, 0.396, np.nan]]),
    )

    np.testing.assert_allclose(actual.t, expected.t)
    np.testing.assert_allclose(actual.depletion, expected.depletion)


def test_read_groundwater_depletion_two_files(tmp_path):
    """
    Test can get GroundwaterDepletion from two CSVs.
    """
    # Prep first GWD input file.
    tmpfl1 = tmp_path / "gwd_1.csv"
    tmpfl1.write_text(
        "year,mm\n1941.902,0.396\n1941.902,0.396\n1942.542,0.396\n1942.542,0.396"
    )
    # Prep second GWD input file.
    tmpfl2 = tmp_path / "gwd_2.csv"
    tmpfl2.write_text(
        "year,mm\n1951.216,0.12\n1951.457,0.51\n1951.618,0.9\n1951.779,0.105"
    )

    actual = read_groundwater_depletion([tmpfl1, tmpfl2])

    expected = GroundwaterDepletion(
        t=np.array(
            [
                [1941.902, 1941.902, 1942.542, 1942.542, np.nan],
                [1951.216, 1951.457, 1951.618, 1951.779, np.nan],
            ]
        ),
        depletion=np.array(
            [[0.396, 0.396, 0.396, 0.396, np.nan], [0.12, 0.51, 0.9, 0.105, np.nan]]
        ),
    )

    np.testing.assert_allclose(actual.t, expected.t)
    np.testing.assert_allclose(actual.depletion, expected.depletion)


def test_read_population_scenarios(tmp_path):
    """
    Test can read PopulationScenarios from a CSV.
    """
    tmpfl = tmp_path / "pop_scen.csv"
    tmpfl.write_text(
        "year,SSP1-Baseline(IMAGE),SSP5-Baseline(REMIND-MAGPIE),SSP2-Baseline(MESSAGE-GLOBIOM),SSP4-Baseline(GCAM4),SSP3-Baseline(AIM/CGE)\n2005,6530547852,6505000000,6503130000,6506642000,6490987900\n2010,6921797852,6894000000,6867390000,6895882000,6879589600",
    )

    actual = read_population_scenarios(tmpfl)

    expected = PopulationScenarios(
        yr=np.array([2005.0, 2010.0]),
        scenarios=np.array(
            [
                [6.530548e09, 6.505000e09, 6.503130e09, 6.506642e09, 6.490988e09],
                [6.921798e09, 6.894000e09, 6.867390e09, 6.895882e09, 6.879590e09],
            ]
        ),
    )

    np.testing.assert_allclose(actual.yr, expected.yr)
    np.testing.assert_allclose(actual.scenarios, expected.scenarios)
