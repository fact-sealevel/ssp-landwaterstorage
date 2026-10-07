import numpy as np
import pytest

from ssp_landwaterstorage.core import (
    Fingerprints,
    Locations,
    map_RCP_to_SSP,
    map_SSPRC_to_SSP,
    map_scenario,
    PopulationHistory,
    ReservoirImpoundment,
    GroundwaterDepletion,
    PopulationScenarios,    
    preprocess

)


def test_fingerprints_interpolate_coefficients():
    """
    Test that we can interplate fingerprint coefficients to Locations.
    """
    sites = Locations(
        name=np.array(["a", "b"]),
        id=np.array([1, 2]),
        lat=np.array([42.5, 47.5]),
        lon=np.array([15.0, 22.5]),
    )
    fprints = Fingerprints(
        fp=np.array(
            [
                [350.0, 600.0, 850.0],
                [250.0, 500.0, 750.0],
                [150.0, 400.0, 650.0],
            ]
        ),
        lat=np.array([40.0, 45.0, 50.0]),
        lon=np.array([10.0, 20.0, 30.0]),
    )

    actual = fprints.interpolate_coefficients(sites)

    expected = np.array([4.25, 5.125])

    np.testing.assert_allclose(actual, expected)


def test_rcp_scenario_maps_correctly():
    """
    Test that RCP scenarios are correctly mapped to SSP scenarios.
    """

    assert map_RCP_to_SSP("rcp26") == "ssp1"
    assert map_RCP_to_SSP("rcp45") == "ssp2"
    assert map_RCP_to_SSP("rcp60") == "ssp4"
    assert map_RCP_to_SSP("rcp85") == "ssp5"


def test_ssprc_scenario_maps_correctly():
    """
    Test that SSP-RC scenarios are correctly mapped to SSP scenarios.
    """

    assert map_SSPRC_to_SSP("ssp119") == "ssp1"
    assert map_SSPRC_to_SSP("ssp245") == "ssp2"
    assert map_SSPRC_to_SSP("ssp460") == "ssp4"
    assert map_SSPRC_to_SSP("ssp585") == "ssp5"


def test_map_scen_routes_correctly_to_rcp():
    """
    Test that map_scenario routes RCP scenarios correctly to SSP scenarios.
    """
    assert map_scenario("rcp26") == "ssp1"
    assert map_scenario("rcp45") == "ssp2"
    assert map_scenario("rcp60") == "ssp4"
    assert map_scenario("rcp85") == "ssp5"


def test_map_scen_routes_correctly_to_ssprc():
    """
    Test that map_scenario routes SSP-RC scenarios correctly to SSP scenarios.
    """
    assert map_scenario("ssp119") == "ssp1"
    assert map_scenario("ssp245") == "ssp2"
    assert map_scenario("ssp460") == "ssp4"
    assert map_scenario("ssp585") == "ssp5"


# def test_map_scen_calls_correct_map_fn_for_rcp():


def test_map_rcp_to_ssp_raises_exception_for_invalid_scenario():
    """
    Test that an exception is raised for an invalid RCP scenario.
    """
    with pytest.raises(ValueError, match="rcp99") as exc_info:
        map_RCP_to_SSP("rcp99")
    assert "scenario does not have a preferred SSP combination." in str(exc_info.value)


def test_map_ssprc_to_ssp_raises_exception_for_invalid_scenario():
    """
    Test that an exception is raised for an invalid SSP-RC scenario.
    """
    with pytest.raises(ValueError, match="ssp999") as exc_info:
        map_SSPRC_to_SSP("ssp999")

    assert (
        "scenario does not have a corresponding ssp-radiative forcing combination."
        in str(exc_info.value)
    ), f"Unexpected exception message: {exc_info.value}"


def test_map_rcp_to_ssp_raises_exception_for_non_rcp_scenario():
    """
    Test that an exception is raised for a non-RCP scenario.
    """
    with pytest.raises(Exception) as exc_info:
        map_RCP_to_SSP("ssp1")
    assert "scenario does not have a preferred SSP combination." in str(
        exc_info.value
    ), f"Unexpected exception message: {exc_info.value}"


def tests_preprocess_dicts_have_correct_keys():

    pophist = PopulationHistory(
        t=np.array([2000, 2001]), 
        pop=np.array([1e6, 1.1e6]),
        pop0=np.array([1e6, 1.1e6]),
        t0=np.array([2000, 2001])
    )
    dams = ReservoirImpoundment(
        t=np.array([2000, 2001]), impoundment=np.array([0, 0.1]))
    popscen = PopulationScenarios(
        yr=np.array([2000, 2001]),
        scenarios=np.array([[1e6, 1.1e6], [1.2e6, 1.3e6]]),
    )
    gwd = GroundwaterDepletion(
        t=np.array([[2000, 2001], [2000, 2001]]), depletion=np.array([[0, 0.1], [0, 0.2]]))
    scenario = "ssp1"
    dotriangular = 0
    out_data, out_conf = preprocess(
        pophist,
        dams,
        popscen,
        gwd,
        scenario,
        dotriangular,
        baseyear=2000,
        pyear_start=2020,
        pyear_end=2100,
        pyear_step=10,
    )
    assert set(out_data.keys()) == {
        "t","pop",
        "tdams","tgwd",
        "gwd", "dams",
        "popscen","popscenyr"}
    assert set(out_conf.keys()) == {
        "dgwd_dt_dpop_pcterr",
        "dam_pcterr",
        "yrs","scen",
        "dotriangular","baseyear",
        "pop0","t0",
        "targyears"}

