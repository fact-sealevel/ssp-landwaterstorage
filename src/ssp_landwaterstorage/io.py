"""
Logic for application IO.
"""

import csv
import os
import re
import time
from typing import Sequence

import numpy as np
from netCDF4 import Dataset
import xarray as xr

from ssp_landwaterstorage.core import (
    PopulationHistory,
    ReservoirImpoundment,
    GroundwaterDepletion,
    PopulationScenarios,
    Locations,
    Fingerprints,
)


def read_locations(fl: str | os.PathLike) -> Locations:
    """
    Read locations from file.
    """
    # Initialize variables to hold data and site information
    names = []
    ids = []
    lats = []
    lons = []

    # Compile the regex for finding commented lines
    comment_regex = re.compile(r"^#")

    # Open the rate file
    with open(fl, "r") as f:
        # Loop over the lines of the file
        for line in f:
            # Skip commented lines
            if re.search(comment_regex, line):
                continue

            # Split the line into components
            (this_name, this_id, this_lat, this_lon) = line.split("\t")

            # Store the information
            names.append(this_name)
            ids.append(int(this_id))
            lats.append(float(this_lat))
            lons.append(float(this_lon))

    out = Locations(
        name=np.array(names),
        id=np.array(ids),
        lat=np.array(lats),
        lon=np.array(lons),
    )
    return out


def read_population_history(pophist_file: str | os.PathLike) -> PopulationHistory:
    """Read population history from file"""
    with open(pophist_file, "r", newline="") as csvfile:
        popdata = csv.reader(csvfile)
        row_count = sum(1 for row in popdata)

    with open(pophist_file, "r", newline="") as csvfile:
        popdata = csv.reader(csvfile)
        _ = next(popdata)
        i = 0
        t = np.zeros(row_count - 1)
        pop = np.zeros(row_count - 1)

        for row in popdata:
            t[i] = row[0]  # store years
            pop[i] = row[1]  # store population
            i += 1

    out = PopulationHistory(
        t=t[::5],  # Sampled with 5 year steps
        pop=pop[::5],
        t0=t,
        pop0=pop,
    )

    return out


def read_reservoir_impoundment(
    reservoir_file: str | os.PathLike,
) -> ReservoirImpoundment:
    """Read reservoir impoundment from file"""
    with open(reservoir_file, "r", newline="") as csvfile:
        damdata = csv.reader(csvfile)
        row_count = sum(1 for row in damdata)

    with open(reservoir_file, "r", newline="") as csvfile:
        damdata = csv.reader(csvfile)
        _ = next(damdata)
        i = 0
        tdams = dams = np.zeros(row_count - 1)
        dams = np.zeros(row_count - 1)

        for row in damdata:
            tdams[i] = row[0]  # store years
            dams[i] = row[1]  # store reservoir impoundment
            i += 1

    out = ReservoirImpoundment(
        t=tdams,
        impoundment=dams,
    )
    return out


def read_groundwater_depletion(
    gwd_files: Sequence[str | os.PathLike],
) -> GroundwaterDepletion:
    """Read groundwater depletion data from file"""

    # Define function to count lines in a .csv file
    def countlines(f):
        with open(f, "r", newline="") as csvfile:
            gwddata = csv.reader(csvfile)
            row_count = sum(1 for row in gwddata)
        return row_count

    # Count the lines in all the GWD files
    nlines = [countlines(f) for f in gwd_files]

    # Initialize a multi-dimensional array to store GWD data
    # TODO: Isn't this counting the file header as part of nlines so get nans at end of these arrays?
    gwd = np.full((len(gwd_files), np.max(nlines)), np.nan)
    tgwd = np.full((len(gwd_files), np.max(nlines)), np.nan)

    for j, p in enumerate(gwd_files):
        with open(p, "r", newline="") as csvfile:
            gwddata = csv.reader(csvfile)
            _ = next(gwddata)
            i = 0

            for row in gwddata:
                tgwd[j, i] = row[0]  # store years
                gwd[j, i] = row[1]  # store gwd
                i += 1

    out = GroundwaterDepletion(
        t=tgwd,
        depletion=gwd,
    )

    return out


def read_population_scenarios(popscen_file: str | os.PathLike) -> PopulationScenarios:
    """Read population scenarios from file"""
    with open(popscen_file, "r", newline="") as csvfile:
        popdata = csv.reader(csvfile)
        row_count = sum(1 for row in popdata)

    with open(popscen_file, "r", newline="") as csvfile:
        popdata = csv.reader(csvfile)
        _ = next(popdata)
        i = 0
        popscenyr = np.zeros(row_count - 1)
        popscen = np.zeros([row_count - 1, 5])  # 5 SSPs

        for row in popdata:
            popscenyr[i] = row[0]  # store years
            popscen[i, :] = row[1:6]  # store population projections
            i += 1

    out = PopulationScenarios(
        yr=popscenyr,
        scenarios=popscen,
    )
    return out


def read_fingerprints(fl: str | os.PathLike) -> Fingerprints:
    """
    Read Fingerprints from NetCDF.
    """
    nc_fid = Dataset(fl, "r")
    out = Fingerprints(
        fp=nc_fid.variables["GROUND"][0, :, :],
        lat=nc_fid.variables["lat"][:],
        lon=nc_fid.variables["lon"][:],
    )
    return out


def write_gslr(
    fl: str | os.PathLike,
    *,
    lwssamps,
    targyears,
    n_samps,
    pipeline_id,
    baseyear,
    scenario,
) -> None:
    """
    Write global sealevel rise data to a NetCDF4 file.
    """
    # Write the total global projections to a netcdf file
    rootgrp = Dataset(fl, "w", format="NETCDF4")

    # Define Dimensions
    _year_dim = rootgrp.createDimension("years", len(targyears))
    _samp_dim = rootgrp.createDimension("samples", n_samps)
    _loc_dim = rootgrp.createDimension("locations", 1)

    # Populate dimension variables
    year_var = rootgrp.createVariable("years", "i4", ("years",))
    samp_var = rootgrp.createVariable("samples", "i8", ("samples",))
    loc_var = rootgrp.createVariable("locations", "i8", ("locations",))
    lat_var = rootgrp.createVariable("lat", "f4", ("locations",))
    lon_var = rootgrp.createVariable("lon", "f4", ("locations",))

    # Create a data variable
    samps = rootgrp.createVariable(
        "sea_level_change",
        "f4",
        ("samples", "years", "locations"),
        zlib=True,
        complevel=4,
    )

    # Assign attributes
    rootgrp.description = "Global SLR contribution from land water storage according to Kopp 2014 workflow"
    rootgrp.history = "Created " + time.ctime(time.time())
    rootgrp.source = "FACTS: {0}".format(pipeline_id)
    rootgrp.baseyear = baseyear
    rootgrp.scenario = scenario
    samps.units = "mm"

    # Put the data into the netcdf variables
    year_var[:] = targyears
    samp_var[:] = np.arange(0, n_samps)
    samps[:, :, :] = lwssamps.T[:, :, np.newaxis]
    lat_var[:] = np.inf
    lon_var[:] = np.inf
    loc_var[:] = -1

    # Close the netcdf
    rootgrp.close()


def write_lslr(
    fl: str | os.PathLike,
    *,
    local_sl,
    targyears,
    n_samps,
    baseyear,
    scenario,
    locations: Locations,
) -> None:
    """
    Write local sealevel rise data to a NetCDF4 file.
    """
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
            "lat": (("locations"), locations.lat),
            "lon": (("locations"), locations.lon),
        },
        coords={
            "years": targyears,
            "locations": locations.id,
            "samples": np.arange(n_samps),
        },
        attrs=ncvar_attributes,
    )

    lws_out.to_netcdf(
        fl,
        encoding={
            "sea_level_change": {
                "dtype": "f4",
                "zlib": True,
                "complevel": 4,
                "_FillValue": nc_missing_value,
            }
        },
    )
    pass
