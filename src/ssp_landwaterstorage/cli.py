"""
Logic for the CLI.
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

import click


@click.command()
@click.option("--scenario", envvar="SSP_LANDWATERSTORAGE_SCENARIO")
@click.option("--dotriangular", envvar="SSP_LANDWATERSTORAGE_DOTRIANGULAR")
@click.option("--includepokherl", envvar="SSP_LANDWATERSTORAGE_INCLUDEPOKHERL")
@click.option("--baseyear", envvar="SSP_LANDWATERSTORAGE_BASEYEAR")
@click.option("--pyear-start", envvar="SSP_LANDWATERSTORAGE_PYEAR_START")
@click.option("--pyear-end", envvar="SSP_LANDWATERSTORAGE_PYEAR_END")
@click.option("--pyear-step", envvar="SSP_LANDWATERSTORAGE_PYEAR_STEP")
@click.option("--nsamps", envvar="SSP_LANDWATERSTORAGE_NSAMPS")
@click.option("--seed", envvar="SSP_LANDWATERSTORAGE_SEED")
@click.option("--pipeline-id", envvar="SSP_LANDWATERSTORAGE_PIPELINE_ID")
@click.option("--dcyear-start", envvar="SSP_LANDWATERSTORAGE_DCYEAR_START")
@click.option("--dcyear-end", envvar="SSP_LANDWATERSTORAGE_DCYEAR_END")
@click.option("--dcrate-lo", envvar="SSP_LANDWATERSTORAGE_DCRATE_LO")
@click.option("--dcrate-hi", envvar="SSP_LANDWATERSTORAGE_DCRATE_HI")
@click.option("--locationfile", envvar="SSP_LANDWATERSTORAGE_LOCATIONFILE")
@click.option("--chunksize", envvar="SSP_LANDWATERSTORAGE_CHUNKSIZE")
def main(
    scenario,
    dotriangular,
    includepokherl,
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
    locationfile,
    chunksize,
) -> None:
    click.echo("Hello from ssp-landwaterstorage!")
    ssp_preprocess_landwaterstorage(
        scenario,
        dotriangular,
        includepokherl,
        baseyear,
        pyear_start,
        pyear_end,
        pyear_step,
        pipeline_id,
    )
    ssp_fit_landwaterstorage(pipeline_id)
    ssp_project_landwaterstorage(
        nsamps, seed, dcyear_start, dcyear_end, dcrate_lo, dcrate_hi, pipeline_id
    )
    ssp_postprocess_landwaterstorage(locationfile, chunksize, pipeline_id)
