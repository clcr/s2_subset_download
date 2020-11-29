# s2_subset_download
A script for downloading and stacking subsets of Sentinel 2 images hosted as cloud-optimised geotifs, hosted on https://registry.opendata.aws/sentinel-2-l2a-cogs/

# Requirements
Pyeo: github.com/clcr/pyeo

# Setup
Clone repository, then fill out `creds.conf` with Scihub username and password.

# Use
The below will download every S2 image of Wuhan between the 2nd and the 19th of July 2020 to the folder ~/wuhan_images/.
Each image will be named yyyy-mm-dd_aoiname.tif, and will be a 4-band geotif in the local UTM projection.
```bash
python download_s2_aoi Wuhan_AOI.shp 2020-07-02 2020-07-19 ~/wuhan_images
