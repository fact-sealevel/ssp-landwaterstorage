# ssp_landwaterstorage

Build the ssp-landwaterstorage container from this repository by cloning the repository and running

```shell
docker build -t ssp-landwaterstorage:dev .
```

from the repository root.

See help documentation for the ssp-landwaterstorage container commands by running:
```shell
docker run --rm ssp-landwaterstorage:dev --help
```

You can then run `ssp-landwaterstorage:dev` like

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

this assumes you have all the required input in `./data/input` and you want output to be written to `./data/output`.

the contents of `location.lst` are locations formatted like

```
New_York	12	40.70	-74.01
```

other input files need to be downloaded and untarred from

- https://zenodo.org/record/7478192/files/ssp_landwaterstorage_postprocess_data.tgz
- https://zenodo.org/record/7478192/files/ssp_landwaterstorage_preprocess_data.tgz
