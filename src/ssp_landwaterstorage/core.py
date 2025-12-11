"""
Core 'business logic'.
"""

from dataclasses import dataclass

import dask.array as da
import numpy as np
from numpy import matlib as mb
from scipy import interpolate
from scipy.stats import norm
from scipy.optimize import curve_fit
from scipy.special import erf


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


def preprocess(
    pophist,
    dams,
    popscen,
    gwd,
    scen,
    dotriangular,
    baseyear,
    pyear_start,
    pyear_end,
    pyear_step,
):
    """ssp_preprocess_landwaterstorage.py

    Code generated 17-09-2019, by Tim Hermans

    This script runs the land water storage pre-processing task for the SSP LWS workflow.
    This task generates the data and variables needed to configure the LWS submodel.

    Parameters:
    scen				The RCP or SSP scenario (default: rcp85)
    dotriangular		Logical 0 or 1, to use triangular distribution for gwd [1,1]
    includepokhrel		Logical 0 or 1, to include Pokhrel data for gwd [1,1]
    pipeline_id			Unique identifier for the pipeline running this module

    Output:
    "%PIPELINE_ID%_data.pkl" = Contains the LWS data
    "%PIPELINE_ID%_config.pkl" = Contains the configuration parameters

    Note: %PIPELINE_ID% is replaced with 'pipeline_id' at run time
    """
    ##################################################
    # configure run (could be separate script)
    dgwd_dt_dpop_pcterr = 0.25  # error on gwd slope
    dam_pcterr = 0.25  # error on sigmoidal function reservoirs
    # baseyear = 2005					# Base year to which projetions are centered
    yrs = np.arange(pyear_start, pyear_end + 1, pyear_step)  # target years projections
    yrs = np.union1d(yrs, baseyear)

    # # paths to data
    # pophist_file = "UNWPP2012 population historical.csv"
    # reservoir_file = "Chao2008 groundwater impoundment.csv"
    # gwd_files = ["Konikow2011 GWD.csv", "Wada2012 GWD.csv", "Pokhrel2012 GWD.csv"]
    # popscen_file = "ssp_iam_baseline_popscenarios2100.csv"

    ###################################################
    # Store the data in a pickle
    output = {
        "t": pophist.t,
        "pop": pophist.pop,
        "tdams": dams.t,
        "dams": dams.impoundment,
        "tgwd": gwd.t,
        "gwd": gwd.depletion,
        "popscen": popscen.scenarios,
        "popscenyr": popscen.yr,
    }

    # Store the configuration in a pickle
    output_conf = {
        "dgwd_dt_dpop_pcterr": dgwd_dt_dpop_pcterr,
        "dam_pcterr": dam_pcterr,
        "yrs": yrs,
        "scen": scen,
        "dotriangular": dotriangular,
        "pop0": pophist.pop0,
        "t0": pophist.t0,
        "baseyear": baseyear,
        "targyears": yrs,
    }

    return output, output_conf


def extend_pop(popscen, popscenyrs):
    # Rate as a function of population scenario (in percent)
    # Obtained from https://www.un.org/development/desa/pd/sites/www.un.org.development.desa.pd/files/files/documents/2020/Jan/un_2002_world_population_to_2300.pdf
    # Table 1, page 14 (pdf page 28)
    rates = (
        np.array(
            [
                [
                    0.76,
                    0.04,
                    -0.46,
                    -0.74,
                    -0.75,
                    -0.60,
                    -0.48,
                    -0.38,
                    -0.32,
                    -0.31,
                    -0.31,
                    -0.32,
                ],
                [
                    1.03,
                    0.51,
                    0.13,
                    -0.07,
                    -0.15,
                    -0.11,
                    -0.03,
                    0.03,
                    0.06,
                    0.06,
                    0.05,
                    0.05,
                ],
                [
                    1.28,
                    0.96,
                    0.64,
                    0.46,
                    0.35,
                    0.36,
                    0.45,
                    0.51,
                    0.54,
                    0.54,
                    0.54,
                    0.54,
                ],
            ]
        )
        / 100
        + 1
    )

    # Extend these rates over the 25-year period they represent
    ext_rates = np.repeat(rates, 25, axis=1)
    ext_years = np.arange(2001, 2301)  # Rates are for years 2001 - 2300

    # SSP map to population scenario
    # "popscen" is sorted in terms of lowest to highest projected population, which is
    # SSP1, SSP5, SSP2, SSP4, SSP3
    scenario_map = np.array([0, 0, 1, 1, 2])

    # Select the appropriate rates
    scenario_rates = ext_rates[scenario_map, :].T

    # Which year in the extended years matches the next population year
    # Note: SSP projection data should end in year 2100
    year_idx = np.flatnonzero(ext_years == popscenyrs[-1]) + 1

    # Initialize variables to hold the extended population and years
    # These will be appended to popscen and popscenyrs provided
    ext_pop = []
    ext_yrs = []

    # Set the initial population
    pop0 = popscen[-1, :]

    # Loop over the extended years
    for i in np.arange(year_idx, len(ext_years)):
        # Calculate the population for this year
        ext_pop.append(pop0 * scenario_rates[i, :])

        # Set the current population for the next iteration
        pop0 = np.array(ext_pop[int(i - year_idx)])

        # Append this year to the extended years
        ext_yrs.append(ext_years[i])

    # Cast boundary rates and years from a list into a numpy arrays
    ext_pop = np.array(ext_pop)
    ext_yrs = np.array(ext_yrs)

    # Append the extension onto the original data
    popscen = np.concatenate((popscen, ext_pop), axis=0)
    popscenyrs = np.concatenate((popscenyrs, ext_yrs))

    return (popscen, popscenyrs)


def fit(my_data, my_config, pipeline_id):
    """ssp_fit_landwaterstorage.py

    Code generated 16-09-2019, by Tim Hermans

    This script runs the land water storage fitting task for the SSP LWS workflow.
    This task fits a linear relation between historical population data and groundwater
    depletion, and a sigmoidal relation between population and reservoir impoundment.

    Parameters:
    pipeline_id = Unique identifier for the pipeline running this code

    Output:
    "%PIPELINE_ID%_fit.pkl" = Pickle file that contains the fitted submodel information

    """
    t = my_data["t"]
    pop = my_data["pop"]
    tdams = my_data["tdams"]
    dams = my_data["dams"]
    tgwds = my_data["tgwd"]
    gwds = my_data["gwd"]
    popscenyr = my_data["popscenyr"]
    popscen = my_data["popscen"]

    t0 = my_config["t0"]
    pop0 = my_config["pop0"]
    dgwd_dt_dpop_pcterr = my_config["dgwd_dt_dpop_pcterr"]
    yrs = my_config["yrs"]
    _ = my_config["scen"]
    dotriangular = my_config["dotriangular"]

    # interpolate reservoir years to population history years t0
    dams = np.interp(t0, tdams, dams)

    # optimisation problem, least squares of fitting dams with sigmoidal function of population
    def sigmoidal(pop0, a, b, c, I0):
        return a * erf((pop0 / 1e6 - b) / c) + I0  # see Kopp et al. 2014 eq.1

    # initial guess
    pinit = np.array([max(dams) / 2, 1, 1, max(dams) / 2])
    # curve fit
    dams_popt, dams_pcov = curve_fit(sigmoidal, pop0, dams, p0=pinit)

    # Initialize variables
    dgwd_dt_dpop_all = []  # change of gwd rate w.r.t. population
    dgwd_dt_all = []  # gwd rate
    pop2gwd_all = []  # population

    # Loop over each of the GWD files' data
    for i in np.arange(gwds.shape[0]):
        # Working with these particular data
        gwd = gwds[i, :]
        tgwd = tgwds[i, :]

        # Remove entries where either tgwd or gwd are "nan"
        inds = np.intersect1d(
            np.flatnonzero(~np.isnan(tgwd)), np.flatnonzero(~np.isnan(gwd))
        )
        tgwd = tgwd[inds]
        gwd = gwd[inds]

        # remove duplicate years
        tgwd, ui = np.unique(tgwd, return_index=True)
        gwd = gwd[ui]

        # interpolate to population history years t (5 year samples), without etrapolating outside bounds
        bound = np.where((tgwd[0] <= t) & (t <= tgwd[-1]))
        bound = bound[0]
        gwd = np.interp(t[bound], tgwd, gwd)

        dgwd_dt = np.diff(gwd) / np.diff(t[bound])  # compute dgwd/dt
        pop2gwd = (
            (pop[bound[0 : len(bound) - 1]] + pop[bound[1 : len(bound)]]) / 2
        )  # get the population at the timesteps between timesteps at which there is GWD information
        dgwd_dt_dpop = np.linalg.lstsq(
            np.transpose([pop2gwd]), np.transpose([dgwd_dt]), rcond=None
        )  # solve least squares linear fit for the change of ground depletion rate with population

        # store dgwd_dt, dgwd_dt_dpop, pop2gwd
        dgwd_dt_dpop_all = np.concatenate((dgwd_dt_dpop_all, dgwd_dt_dpop[0][0]))
        dgwd_dt_all.append(dgwd_dt)
        pop2gwd_all.append(pop2gwd)

    # mean and standard deviation dgwd/dt/dpop
    if dotriangular == 0:  # if no triangular distribution
        mean_dgwd_dt_dpop = np.mean(dgwd_dt_dpop_all)
        std_dgwd_dt_dpop = np.sqrt(
            np.std((dgwd_dt_dpop_all), ddof=1) ** 2
            + (mean_dgwd_dt_dpop * dgwd_dt_dpop_pcterr) ** 2
        )

    else:  # if triangular distribution
        mean_dgwd_dt_dpop = np.median(dgwd_dt_dpop_all)
        std_dgwd_dt_dpop = np.array((min(dgwd_dt_dpop_all), max(dgwd_dt_dpop_all)))

    popscenyr0 = popscenyr
    popscen = np.divide(popscen, 1e3)  # convert to thousands
    # popscen = popscen/1000.0

    # if scenarios start >2000, prepend the years from 2000 onward and
    # interpolate historical population up to the start of projections
    if min(popscenyr) > 2000:
        popscenyr = np.insert(popscenyr, 0, range(2000, int(min(popscenyr))))
        popscen = np.concatenate(
            (
                np.transpose(
                    mb.repmat(
                        np.interp(range(2000, int(min(popscenyr0))), t0, pop0), 5, 1
                    )
                ),
                popscen,
            )
        )

    # Extend the population projections
    (popscen, popscenyr) = extend_pop(popscen, popscenyr)

    # Test to make sure the target years are within the projected population years
    if max(yrs) > max(popscenyr):
        raise Exception(
            "Target year {} exceeds the maximum year of SSP population scenarios {}".format(
                max(yrs), max(popscenyr)
            )
        )

    # Store the variables in a pickle
    output = {
        "popscen": popscen,
        "popscenyr": popscenyr,
        "dams_popt": dams_popt,
        "mean_dgwd_dt_dpop": mean_dgwd_dt_dpop,
        "std_dgwd_dt_dpop": std_dgwd_dt_dpop,
    }
    return output


def project(
    my_fit,
    my_config,
    Nsamps,
    rng_seed,
    dcyear_start,
    dcyear_end,
    dcrate_lo,
    dcrate_hi,
):
    """ssp_project_landwaterstorage.py

    Code generated 16-09-2019, by Tim Hermans

    This script runs the land water storage projections for the SSP LWS workflow. This task
    projects the future contribution of groundwater depletion and reservoir impoundment
    to global mean sea level based on the selected SSP of population growth.

    Parameters:
    Nsamps = Number of samples to project
    rng_seed = Seed value for the random number generator
    pipeline_id = Unique identifier for the pipeline running this code

    Output:
    "%PIPELINE_ID%_projections.pkl" = Pickle file that contains the global LWS projections

    """
    popscen = my_fit["popscen"]
    popscenyr = my_fit["popscenyr"]
    dams_popt = my_fit["dams_popt"]
    mean_dgwd_dt_dpop = my_fit["mean_dgwd_dt_dpop"]
    std_dgwd_dt_dpop = my_fit["std_dgwd_dt_dpop"]

    t0 = my_config["t0"]
    pop0 = my_config["pop0"]
    dgwd_dt_dpop_pcterr = my_config["dgwd_dt_dpop_pcterr"]
    dam_pcterr = my_config["dam_pcterr"]
    yrs = my_config["yrs"]
    baseyear = my_config["baseyear"]
    targyears = my_config["targyears"]
    scen = my_config["scen"]
    dotriangular = my_config["dotriangular"]

    # optimisation problem, least squares of fitting dams with sigmoidal function of population
    def sigmoidal(pop0, a, b, c, I0):
        return a * erf((pop0 / 1e6 - b) / c) + I0  # see Kopp et al. 2014 eq.1

    ##################################################
    # select scenario population using target RCP or SSP scenario
    # prefered SSP RCP combinations (correspondence with Aimee)
    RCPtoSSP = {
        "rcp19": "ssp1",
        "rcp26": "ssp1",
        "rcp45": "ssp2",
        "rcp60": "ssp4",
        "rcp70": "ssp3",
        "rcp85": "ssp5",
    }

    # SSP ordered from low to high projections
    SSPorder = {
        "ssp1": 0,
        "ssp5": 1,
        "ssp2": 2,
        "ssp4": 3,
        "ssp3": 4,
    }

    # extract SSP scenario from configured target RCP or SSP scenario
    if scen[0:3] == "rcp":
        targetSSP = RCPtoSSP[scen]
        if scen not in RCPtoSSP:
            raise Exception(
                "Configured RCP scenario does not have a preferred SSP combination."
            )
    else:
        targetSSP = scen

    # draw scenario population from target scenario
    popdraw = popscen[:, SSPorder[targetSSP]]

    # interpolate to annual means
    popdraw = np.interp(np.linspace(2000, 2300, 301), popscenyr, popdraw)
    popscenyr = np.linspace(2000, 2300, 301)

    # random draw functions for reservoirs and gwd

    # symbolic function interpolating the cumulative sum of population for a
    # certain probability x1 times the normal distribution with mean dgwd/dt/dpopmGWD
    # and standard deviation stdGWD defined earlier, onto desired years
    if dotriangular == 0:

        def gwddraw(seed1):
            return np.interp(
                yrs,
                popscenyr,
                np.cumsum(
                    np.multiply(
                        popdraw,
                        (mean_dgwd_dt_dpop + norm.ppf(seed1) * std_dgwd_dt_dpop),
                    )
                ),
            )
    else:

        def gwddraw(seed1, seed2):
            return np.interp(
                yrs,
                popscenyr,
                np.cumsum(
                    np.multiply(
                        popdraw,
                        np.interp(
                            seed1,
                            np.array([0, 0.5, 1]),
                            np.array(
                                [
                                    std_dgwd_dt_dpop[0],
                                    mean_dgwd_dt_dpop,
                                    std_dgwd_dt_dpop[-1],
                                ]
                            ),
                        ),
                    )
                )
                * (1 + norm.ppf(seed2) * dgwd_dt_dpop_pcterr),
            )

    # random draw from reservoir storage: sigmoidal function with
    # randomly drawn population as input (>t=2000, see Kopp 2014)
    # and subtracts the sigmoidal function with the population at t=2000 (this
    # will then be the origin).

    # This is multiplied with a normal distribution with a mean of 1 and a std of
    # 25% (default defined error elated to the impoundment rate. Kopp 2014: 2sigma=50%):
    # - minus sign since reservoir storage leads to GSL drop -

    pop2000 = pop0[t0 == 2000]  # population at 2000

    def damdraw(seed1):  ###decide max of sigmoid or pop2000->choose
        poprand = np.array([popdraw])  # random draw from population
        poprand[poprand < pop2000] = (
            pop2000  # impoundment is not allowed to be reduced below yr 2000 levels (Kopp et al., 2014)
        )

        X = np.multiply(
            -1
            * (
                sigmoidal(
                    poprand, dams_popt[0], dams_popt[1], dams_popt[2], dams_popt[3]
                )
                - sigmoidal(
                    pop2000[0], dams_popt[0], dams_popt[1], dams_popt[2], dams_popt[3]
                )
            ),
            1 + norm.ppf(seed1) * dam_pcterr,
        )

        # X = np.multiply(-1*(sigmoidal(np.array([popdraw(seed1)]),dams_popt[0],dams_popt[1],dams_popt[2],dams_popt[3])\
        #                    - sigmoidal(pop2000[0],dams_popt[0],dams_popt[1],dams_popt[2],dams_popt[3])), 1+norm.ppf(seed2)*dam_pcterr )

        return np.interp(yrs, popscenyr, X[0])

    ##################################################
    # generate seeds and draw samples
    rng = np.random.default_rng(rng_seed)
    if isinstance(Nsamps, int):  # if only given a single number Nsamps
        seeds0 = np.linspace(0, 1, Nsamps + 2)
        seeds0 = seeds0[1:-1]
    else:
        seeds = Nsamps
        seeds0 = Nsamps

    if seeds0.ndim == 1:  # if seeds is a vector
        seeds = np.empty((4, len(seeds0)))
        for j in range(0, 4):
            seeds[j, :] = seeds0[rng.permutation(len(seeds0))]

    # draw the samples
    damsamps = np.empty((len(yrs), Nsamps))
    gwdsamps = np.empty((len(yrs), Nsamps))

    if dotriangular == 0:
        for ii in range(0, np.shape(seeds)[1]):
            damsamps[:, ii] = damdraw(seeds[3, ii])
            gwdsamps[:, ii] = gwddraw(seeds[1, ii])
    else:
        for ii in range(0, np.shape(seeds)[1]):
            damsamps[:, ii] = damdraw(seeds[3, ii])
            gwdsamps[:, ii] = gwddraw(seeds[1, ii], seeds[2, ii])

    # add to total lws equivalent gsl
    # Note: Only 80% of ground water depletion makes it to the ocean
    # Wada et al. 2016
    lwssamps = (gwdsamps * 0.8) + damsamps
    # lwssamps = gwdsamps + damsamps

    # Apply correction for planned dam construction -------------------
    # Which years overlap?
    dc_year_idx = np.flatnonzero(np.logical_and(yrs >= dcyear_start, yrs <= dcyear_end))
    dc_eyear_idx = np.flatnonzero(yrs > dcyear_end)

    # Generate samples of the rates
    dc_rates = rng.uniform(dcrate_lo, dcrate_hi, Nsamps)

    # Expand these rates into sea-level change over time
    dc_samps = np.zeros((len(yrs), Nsamps))
    dc_samps[dc_year_idx, :] += dc_rates[np.newaxis, :] * (
        yrs[dc_year_idx, np.newaxis] - dcyear_start
    )
    dc_samps[dc_eyear_idx, :] = (
        dc_rates[np.newaxis, :] * (dcyear_end - dcyear_start)
    ) * np.ones((len(dc_eyear_idx), 1))

    # Add these dam correction samples back to the projections
    lwssamps += dc_samps

    # -----------------------------------------------------------------

    # Center the samples to the baseyear
    baseyear_idx = np.isin(yrs, baseyear)
    center_values = lwssamps[baseyear_idx, :]
    lwssamps -= center_values

    # Subset for the target years
    targyear_idx = np.isin(yrs, targyears)
    lwssamps = lwssamps[targyear_idx, :]

    return lwssamps


def postprocess(lwssamps, fingerprints: Fingerprints, sites: Locations, chunksize):
    """ssp_postprocess_landwaterstorage.py

    This script runs the land water storage postprocessing task from the SSP module set.
    This task generates localized contributions to sea-level change due to land water storage.

    Parameters:
    locationfile = File that contains points for localization
    pipeline_id = Unique identifier for the pipeline running this code

    Output: NetCDF file containing the local sea-level rise projections
    """
    lwssamps = np.transpose(lwssamps)

    # Apply the fingerprints
    fpsites = da.array(fingerprints.interpolate_coefficients(sites))
    fpsites = fpsites.rechunk(chunksize)

    # Calculate the local sl samples
    local_sl = np.multiply.outer(lwssamps, fpsites)

    return local_sl
