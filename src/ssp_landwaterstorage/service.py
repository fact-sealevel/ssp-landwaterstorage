"""
Services the UI provides to our lovely users.
"""

from ssp_landwaterstorage.ssp_landwaterstorage_preprocess import (
    ssp_preprocess_landwaterstorage,
)
from ssp_landwaterstorage.ssp_landwaterstorage_fit import ssp_fit_landwaterstorage
from ssp_landwaterstorage.ssp_landwaterstorage_project import (
    ssp_project_landwaterstorage,
)
from ssp_landwaterstorage.ssp_landwaterstorage_postprocess import (
    ssp_postprocess_landwaterstorage,
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
    out_data, out_conf = ssp_preprocess_landwaterstorage(
        pophist_file,
        reservoir_file,
        popscen_file,
        gwd_files,
        scenario,
        dotriangular,
        baseyear,
        pyear_start,
        pyear_end,
        pyear_step,
    )
    out_fit = ssp_fit_landwaterstorage(out_data, out_conf, pipeline_id)
    out_proj = ssp_project_landwaterstorage(
        out_fit,
        out_conf,
        nsamps,
        seed,
        dcyear_start,
        dcyear_end,
        dcrate_lo,
        dcrate_hi,
        pipeline_id,
        output_gslr_file,
    )
    ssp_postprocess_landwaterstorage(
        out_proj, fp_file, location_file, chunksize, pipeline_id, output_lslr_file
    )
