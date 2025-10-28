import numpy as np

from ssp_landwaterstorage.io import (
    read_population_history,
    read_population_scenarios,
    read_reservoir_impoundment,
    read_groundwater_depletion,
)

""" ssp_preprocess_landwaterstorage.py

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


def ssp_preprocess_landwaterstorage(
    pophist_file,
    reservoir_file,
    popscen_file,
    gwd_files,
    scen,
    dotriangular,
    baseyear,
    pyear_start,
    pyear_end,
    pyear_step,
):
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

    if len(gwd_files) != 3:
        dotriangular = 0

    pophist = read_population_history(pophist_file)
    dams = read_reservoir_impoundment(reservoir_file)
    gwd = read_groundwater_depletion(gwd_files)
    popscen = read_population_scenarios(popscen_file)

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
