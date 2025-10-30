import numpy as np
import dask.array as da

from ssp_landwaterstorage.io import write_lslr, read_locations, read_fingerprints

""" ssp_postprocess_landwaterstorage.py

This script runs the land water storage postprocessing task from the SSP module set.
This task generates localized contributions to sea-level change due to land water storage.

Parameters:
locationfile = File that contains points for localization
pipeline_id = Unique identifier for the pipeline running this code

Output: NetCDF file containing the local sea-level rise projections

"""


def ssp_postprocess_landwaterstorage(
    my_proj, fp_file, location_file, chunksize, pipeline_id, nc_filename
):
    targyears = my_proj["years"]
    scenario = my_proj["scen"]
    baseyear = my_proj["baseyear"]
    lwssamps = np.transpose(my_proj["lwssamps"])

    # Load the site locations
    sites = read_locations(location_file)

    # Initialize variable to hold the localized projections
    nsamps = lwssamps.shape[0]

    # Apply the fingerprints
    fpsites = da.array(read_fingerprints(fp_file).interpolate_coefficients(sites))
    fpsites = fpsites.rechunk(chunksize)

    # Calculate the local sl samples
    local_sl = np.multiply.outer(lwssamps, fpsites)

    write_lslr(
        nc_filename,
        local_sl=local_sl,
        targyears=targyears,
        n_samps=nsamps,
        baseyear=baseyear,
        scenario=scenario,
        locations=sites,
    )

    return None
