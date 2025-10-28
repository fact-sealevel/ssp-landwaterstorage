"""
Core 'business logic'.
"""

from dataclasses import dataclass

import numpy as np
from scipy import interpolate


@dataclass
class PopulationHistory:
    t: np.ndarray
    pop: np.ndarray
    pop0: np.ndarray
    t0: np.ndarray


@dataclass
class ReservoirImpoundment:
    t: np.ndarray
    impoundment: np.ndarray


@dataclass
class GroundwaterDepletion:
    t: np.ndarray
    depletion: np.ndarray


@dataclass
class PopulationScenarios:
    yr: np.ndarray
    scenarios: np.ndarray


@dataclass
class Locations:
    name: np.ndarray
    id: np.ndarray
    lat: np.ndarray
    lon: np.ndarray


@dataclass
class Fingerprints:
    """Fingerprint coefficients to interpolate to sites."""

    fp: np.ndarray
    lat: np.ndarray
    lon: np.ndarray

    def interpolate_coefficients(self, locations: Locations) -> np.ndarray:
        """
        Assigns interpolated fingerprint coefficients to sites identifieid by the vectors of lats and lons provided

        Parameters
        ----------
        locations: Sites of interest.

        Returns
        -------
        Vector of fingerprint coefficients for the sites of interst.
        """
        qlat = locations.lat  # [-90, 90]
        qlon = locations.lon  # [-180, 180]

        fp_interp = interpolate.RectBivariateSpline(
            self.lat, self.lon, self.fp, kx=1, ky=1
        )
        # TODO: Why divide by 100?
        fp_sites = fp_interp.ev(qlat, np.mod(qlon, 360)) / 100
        return fp_sites
