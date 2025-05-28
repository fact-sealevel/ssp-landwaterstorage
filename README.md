# ssp_landwaterstorage

Build, see help documentation and run from scratch like this:
```shell
docker buildx build -t ssp-landwaterstorage:dev .

docker container run --rm ssp-landwaterstorage:dev --help

docker container run -t --rm \
    -v ./data/input:/mnt/ssp_lws_in:ro \
    -v ./data/output:/mnt/ssp_lws_out \
    --env-file .env \
    ssp-landwaterstorage:dev
```

this assumes you have all the required input in `./data/input` and you want output to be written to `./data/output`.

You can use a .env to set parameters and configuration. For example, the .env file might contain

```dotenv
SSP_LANDWATERSTORAGE_PIPELINE_ID=1234
SSP_LANDWATERSTORAGE_OUTPUT_GSLR_FILE=/mnt/ssp_lws_out/output_gslr.nc
SSP_LANDWATERSTORAGE_OUTPUT_LSLR_FILE=/mnt/ssp_lws_out/output_lslr.nc
SSP_LANDWATERSTORAGE_POPHIST_FILE=/mnt/ssp_lws_in/UNWPP2012_population_historical.csv
SSP_LANDWATERSTORAGE_RESERVOIR_FILE=/mnt/ssp_lws_in/Chao2008_groundwater_impoundment.csv
SSP_LANDWATERSTORAGE_POPSCEN_FILE=/mnt/ssp_lws_in/ssp_iam_baseline_popscenarios2100.csv
SSP_LANDWATERSTORAGE_GWD_FILES=/mnt/ssp_lws_in/Konikow2011_GWD.csv /mnt/ssp_lws_in/Wada2012_GWD.csv /mnt/ssp_lws_in/Pokhrel2012_GWD.csv
SSP_LANDWATERSTORAGE_FP_FILE=/mnt/ssp_lws_in/REL_GROUNDWATER_NOMASK.nc
SSP_LANDWATERSTORAGE_LOCATION_FILE=/mnt/ssp_lws_in/location.lst
```

the contents of `location.lst` are 

```
New_York	12	40.70	-74.01
```

other input files need to be downloaded and untarred from

- https://zenodo.org/record/7478192/files/ssp_landwaterstorage_postprocess_data.tgz
- https://zenodo.org/record/7478192/files/ssp_landwaterstorage_preprocess_data.tgz
- 
The spaces in the file names need to be replaced with underscores (`_`).