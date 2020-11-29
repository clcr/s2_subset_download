import os
import configparser

from s2_cog_functions import download_s2_subset

aoi_file = "Wuhan_AOI.shp"
date_start = "20200702"
date_end = "20200719"
out_dir = "."
bands = ["B02", "B03", "B04", "B08"]
conf = configparser.ConfigParser()
conf.read('creds.conf')
download_s2_subset(aoi_file, date_start, date_end, out_dir, bands, conf)
assert os.path.exists("2020-07-06_Wuhan_AOI.tif")
assert os.path.exists("2020-07-08_Wuhan_AOI.tif")