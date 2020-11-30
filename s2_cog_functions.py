"""Initial test of a cloud-optimised geotif access for S2"""

import osgeo.gdal as gdal
import osgeo.ogr as ogr
import numpy as np
import os
from os import path as p
from tempfile import TemporaryDirectory

import matplotlib.pyplot as plt
from pyeo import queries_and_downloads as qry
from pyeo import coordinate_manipulation as coord
from pyeo import raster_manipulation as ras

import pdb

# Pil wants RGP pixels 

s2_resolutions = {
        "B01":60,
        "B02":10,
        "B03":10,
        "B04":10,
        "B05":20,
        "B06":20,
        "B07":20,
        "B08":10,
        "B8a":20,
        "B09":60,
        "B10":60,
        "B11":20,
        "B12":20}


def build_aws_path(product, band='B02'):
    date = product["beginposition"]
    # cogs id: S2A_30QYD_20200322_0_L2A
    # s2_id : S2A_MSIL1C_20200708T025551_N0209_R032_T50RKV_20200708T055708
    platform, _, _, _, _, orbit, _ = product['identifier'].split('_')
    orbit = orbit[1:]
    cogs_id = "_".join((platform, orbit, date.strftime("%Y%m%d"), '0', 'L2A'))
    s3_path = "/".join((orbit[0:2], orbit[2], orbit[3:5], str(date.year), str(date.month), cogs_id))
    s3_path = "http://sentinel-cogs.s3.amazonaws.com/sentinel-s2-l2a-cogs/" + s3_path
    s3_path = s3_path+'/'+band+'.tif'
    return s3_path


def get_subset_image(cog_path, aoi_path, out_path, band):
    this_prod = gdal.Open('/vsicurl/'+cog_path)
    with TemporaryDirectory() as td:
        shp_path = td + "tmp.shp"
        coord.reproject_vector(aoi_path, shp_path, this_prod.GetProjection())
        aoi_wkt = qry.shapefile_to_wkt(shp_path)
    x_min, x_max, y_min, y_max = coord.pixel_bounds_from_polygon(this_prod, aoi_wkt)
    x_size = x_max-x_min
    y_size = y_max-y_min
    image_data = this_prod.ReadAsArray(x_min, y_min, x_size, y_size)
    granule_gt = this_prod.GetGeoTransform()
    x_geo, y_geo = coord.pixel_to_point_coordinates((y_min, x_min), granule_gt)
    res = s2_resolutions[band]
    subset_gt = [x_geo, res, 0, y_geo, 0, res*-1]
    out = ras.save_array_as_image(image_data, out_path, subset_gt, this_prod.GetProjection())
    return out


def download_s2_subset(aoi_file, date_start, date_end, out_dir, bands, conf):
    # TODO: Add cloud cover and output EPSG as variables
    s2_products = qry.check_for_s2_data_by_date(aoi_file,
                                                date_start.strftime("%Y%m%d"),
                                                date_end.strftime("%Y%m%d"),
                                                conf)
    for prod_id, product in s2_products.items():
        with TemporaryDirectory() as td:
            for band in bands:
                temp_path = p.join(td, band + ".tif")
                cog_path = build_aws_path(product, band)
                get_subset_image(cog_path, aoi_file, temp_path, band)
            out_name = p.basename(aoi_file).rsplit('.')[0] + ".tif"
            out_name = str(product["beginposition"].strftime("%Y-%m-%d")) + '_' + out_name
            out_path = p.join(out_dir, out_name)
            ras.stack_images([p.join(td, band + ".tif") for band in bands], out_path)
