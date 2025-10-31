"""
Services the UI provides to our lovely users.
"""

from ssp_landwaterstorage.core import preprocess, fit, project, postprocess
from ssp_landwaterstorage.io import (
    read_fingerprints,
    read_population_history,
    read_population_scenarios,
    read_locations,
    read_reservoir_impoundment,
    read_groundwater_depletion,
    write_gslr,
    write_lslr,
)


def project_landwaterstorage(
    pophist_file,
    reservoir_file,
    popscen_file,
    gwd_files,
    fp_file,
    scenario,
    dotriangular,
    baseyear,
    pyear_start,
    pyear_end,
    pyear_step,
    nsamps,
    seed,
    pipeline_id,
    dcyear_start,
    dcyear_end,
    dcrate_lo,
    dcrate_hi,
    location_file,
    chunksize,
    output_gslr_file,
    output_lslr_file,
) -> None:
    """Project landwaterstorage"""
    pophist = read_population_history(pophist_file)
    dams = read_reservoir_impoundment(reservoir_file)
    gwd = read_groundwater_depletion(gwd_files)
    popscen = read_population_scenarios(popscen_file)

    # Why?
    # Should at least log when this happens.
    if len(gwd_files) != 3:
        dotriangular = 0

    out_data, out_conf = preprocess(
        pophist,
        dams,
        popscen,
        gwd,
        scenario,
        dotriangular,
        baseyear,
        pyear_start,
        pyear_end,
        pyear_step,
    )

    out_fit = fit(out_data, out_conf, pipeline_id)

    gslr = project(
        out_fit,
        out_conf,
        nsamps,
        seed,
        dcyear_start,
        dcyear_end,
        dcrate_lo,
        dcrate_hi,
    )
    write_gslr(
        output_gslr_file,
        targyears=out_conf["targyears"],
        n_samps=nsamps,
        pipeline_id=pipeline_id,
        baseyear=baseyear,
        scenario=scenario,
        lwssamps=gslr,
    )

    sites = read_locations(location_file)
    fingerprints = read_fingerprints(fp_file)
    lslr = postprocess(gslr, fingerprints, sites, chunksize)
    write_lslr(
        output_lslr_file,
        local_sl=lslr,
        targyears=out_conf["targyears"],
        n_samps=nsamps,
        baseyear=baseyear,
        scenario=scenario,
        locations=sites,
    )
