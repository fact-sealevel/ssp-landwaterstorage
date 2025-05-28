import numpy as np
import pickle
import argparse
import time
from ssp_landwaterstorage.read_locationfile import ReadLocationFile
from ssp_landwaterstorage.AssignFP import AssignFP

import xarray as xr
import dask.array as da

""" ssp_postprocess_landwaterstorage.py

This script runs the land water storage postprocessing task from the SSP module set.
This task generates localized contributions to sea-level change due to land water storage.

Parameters:
locationfile = File that contains points for localization
pipeline_id = Unique identifier for the pipeline running this code

Output: NetCDF file containing the local sea-level rise projections

"""


def ssp_postprocess_landwaterstorage(fp_file, location_file, chunksize, pipeline_id):
    # Load the configuration file
    projfile = "{}_projections.pkl".format(pipeline_id)
    try:
        f = open(projfile, "rb")
    except Exception as e:
        print(f"Cannot open projection file {projfile}\n")
        raise e

    # Extract the configuration variables
    my_proj = pickle.load(f)
    f.close()

    targyears = my_proj["years"]
    scenario = my_proj["scen"]
    baseyear = my_proj["baseyear"]
    lwssamps = np.transpose(my_proj["lwssamps"])

    # Load the site locations
    (_, site_ids, site_lats, site_lons) = ReadLocationFile(location_file)

    # Initialize variable to hold the localized projections
    nsamps = lwssamps.shape[0]

    # Apply the fingerprints
    # fp_file = os.path.join(os.path.dirname(__file__), "REL_GROUNDWATER_NOMASK.nc")
    fpsites = da.array(AssignFP(fp_file, site_lats, site_lons))
    fpsites = fpsites.rechunk(chunksize)

    # Calculate the local sl samples
    local_sl = np.multiply.outer(lwssamps, fpsites)

    # Define the missing value for the netCDF files
    nc_missing_value = np.nan  # np.iinfo(np.int16).min

    # Create the xarray data structures for the localized projections
    ncvar_attributes = {
        "description": "Local SLR contributions from land water storage according to Kopp 2014 workflow",
        "history": "Created " + time.ctime(time.time()),
        "source": "SLR Framework: Kopp 2014 workflow",
        "scenario": scenario,
        "baseyear": baseyear,
    }

    lws_out = xr.Dataset(
        {
            "sea_level_change": (
                ("samples", "years", "locations"),
                local_sl,
                {"units": "mm", "missing_value": nc_missing_value},
            ),
            "lat": (("locations"), site_lats),
            "lon": (("locations"), site_lons),
        },
        coords={
            "years": targyears,
            "locations": site_ids,
            "samples": np.arange(nsamps),
        },
        attrs=ncvar_attributes,
    )

    lws_out.to_netcdf(
        "{0}_localsl.nc".format(pipeline_id),
        encoding={
            "sea_level_change": {
                "dtype": "f4",
                "zlib": True,
                "complevel": 4,
                "_FillValue": nc_missing_value,
            }
        },
    )

    return None


if __name__ == "__main__":
    # Initialize the command-line argument parser
    parser = argparse.ArgumentParser(
        description="Run the land water storage postprocessing stage from the SSP module set",
        epilog="Note: This is meant to be run as part of the SSP module set within the Framework for the Assessment of Changes To Sea-level (FACTS)",
    )

    # Define the command line arguments to be expected
    parser.add_argument(
        "--locationfile",
        help="File that contains name, id, lat, and lon of points for localization",
        default="location.lst",
    )
    parser.add_argument(
        "--chunksize",
        help="Number of locations to process at a time [default=50]",
        type=int,
        default=50,
    )
    parser.add_argument(
        "--pipeline_id", help="Unique identifier for this instance of the module"
    )

    # Parse the arguments
    args = parser.parse_args()

    # Run the projection process on the files specified from the command line argument
    ssp_postprocess_landwaterstorage(
        args.locationfile, args.chunksize, args.pipeline_id
    )

    exit()
