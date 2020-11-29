aoi_file = "Wuhan_AOI.shp"
date_start = "20200702"
date_end = "20200719"
out_dir = "."
bands = ["B02", "B03", "B04", "B08"]
download_s2_subset(aoi_file, date_start, date_end, out_dir, bands, conf)