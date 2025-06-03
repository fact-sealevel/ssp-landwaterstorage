# ssp-landwaterstorage

Containerized application projecting groundwater depletion and dam impoundment contributions to sea level. See IPCC AR6 WG1 9.6.3.2.6.

> [!CAUTION]
> This is a prototype. It is likely to change in breaking ways. It might delete all your data. Don't use it in production.

## Example

First, create a new directory, download required input data and prepare for the run, like

```shell
# Input data we will pass to the container
mkdir -p ./data/input
curl -sL https://zenodo.org/record/7478192/files/ssp_landwaterstorage_postprocess_data.tgz | tar -zx -C ./data/input
curl -sL https://zenodo.org/record/7478192/files/ssp_landwaterstorage_preprocess_data.tgz | tar -zx -C ./data/input

echo "New_York	12	40.70	-74.01" > ./data/input/location.lst

# Output projections will appear here
mkdir -p ./data/output
```

Now run the container, for example with Docker, like

```shell
docker run --rm \
    -v ./data/input:/mnt/ssp_lws_in:ro \
    -v ./data/output:/mnt/ssp_lws_out \
    ssp-landwaterstorage:dev \
    --pipeline-id=1234 \
    --output-gslr-file="/mnt/ssp_lws_out/output_gslr.nc" \
    --output-lslr-file="/mnt/ssp_lws_out/output_lslr.nc" \
    --location-file="/mnt/ssp_lws_in/location.lst" \
    --pophist-file="/mnt/ssp_lws_in/UNWPP2012 population historical.csv" \
    --reservoir-file="/mnt/ssp_lws_in/Chao2008 groundwater impoundment.csv" \
    --popscen-file="/mnt/ssp_lws_in/ssp_iam_baseline_popscenarios2100.csv" \
    --gwd-file="/mnt/ssp_lws_in/Konikow2011 GWD.csv" \
    --gwd-file="/mnt/ssp_lws_in/Wada2012 GWD.csv" \
    --gwd-file="/mnt/ssp_lws_in/Pokhrel2012 GWD.csv" \
    --fp-file="/mnt/ssp_lws_in/REL_GROUNDWATER_NOMASK.nc"
```

## Features

Several options and configurations are available when running the container.

```shell
Usage: ssp-landwaterstorage [OPTIONS]

  Project groundwater depletion and dam impoundment contributions to sea
  level. See IPCC AR6 WG1 9.6.3.2.6.

Options:
  --pipeline-id TEXT           Unique identifier for this instance of the
                               module.  [required]
  --output-gslr-file TEXT      Path to write output global SLR file.
                               [required]
  --output-lslr-file TEXT      Path to write output local SLR file.
                               [required]
  --pophist-file TEXT          Path to the historical population file.
                               [required]
  --reservoir-file TEXT        Path to the groundwater impoundment file.
                               [required]
  --popscen-file TEXT          Path to the population scenario file.
                               [required]
  --gwd-file TEXT              Path to groundwater depletion file.  [required]
  --fp-file TEXT               Path to fingerprint file.  [required]
  --location-file TEXT         File containing name, id, lat, and lon of
                               points for localization.  [required]
  --scenario TEXT              Use RCP or SSP scenario.
  --dotriangular BOOLEAN       Use triangular distribution for GWD.
  --includepokherl BOOLEAN     Include Pokhrl data for GWD.
  --baseyear INTEGER RANGE     Base year to which projections are centered.
                               [2000<=x<=2010]
  --pyear-start INTEGER RANGE  Year for which projections start.  [x>=2000]
  --pyear-end INTEGER RANGE    Year for which projections end.  [x<=2300]
  --pyear-step INTEGER RANGE   Step size in years between start and end at
                               which projections are produced.  [x>=1]
  --nsamps INTEGER             Number of samples to generate.
  --seed INTEGER               Seed value for random number generator.
  --dcyear-start INTEGER       Year in which dam correction application is
                               started.
  --dcyear-end INTEGER         Year in which dam correction application is
                               ended.
  --dcrate-lo FLOAT            Lower bound of dam correction rate.
  --dcrate-hi FLOAT            Upper bound of dam correction rate.
  --chunksize INTEGER          Number of locations to process at a time.
  --help                       Show this message and exit.
```

See this help documentation by running:
```shell
docker run --rm ssp-landwaterstorage:dev --help
```

These options and configurations can also be set with environment variables prefixed by `SSP_LANDWATERSTORAGE_*`. For example, set `--pophist-file` with as an environment variable with `SSP_LANDWATERSTORAGE_POPHIST_FILE`.

## Building the container locally

You can build the container with Docker by cloning the repository locally and then running

```shell
docker build -t ssp-landwaterstorage:dev .
```

from the repository root.

## Support

Source code is available online at https://github.com/stcaf-org/ssp-landwaterstorage. This software is open source and available under the MIT license.

Please file issues in the issue tracker at https://github.com/stcaf-org/ssp-landwaterstorage/issues.