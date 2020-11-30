import os
import configparser
import datetime as dt

from s2_cog_functions import download_s2_subset

aoi_file = "Wuhan_AOI.shp"
date_start = dt.datetime.strptime("20200702", "%Y%m%d")
date_end = dt.datetime.strptime("20200719", "%Y%m%d")
out_dir = "."
bands = ["B02", "B03", "B04", "B08"]
conf = configparser.ConfigParser()
conf.read('creds.conf')
download_s2_subset(aoi_file, date_start, date_end, out_dir, bands, conf)
assert os.path.exists("Wuhan_AOI_2020-07-06.tif")
assert os.path.exists("Wuhan_AOI_2020-07-08.tif")