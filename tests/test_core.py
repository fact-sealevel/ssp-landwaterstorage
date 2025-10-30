import numpy as np

from ssp_landwaterstorage.core import Fingerprints, Locations


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
