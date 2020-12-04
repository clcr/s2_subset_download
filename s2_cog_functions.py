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

s2_resolutions = {
        "B01": 60,
        "B02": 10,
        "B03": 10,
        "B04": 10,
        "B05": 20,
        "B06": 20,
        "B07": 20,
        "B08": 10,
        "B8a": 20,
        "B09": 60,
        "B10": 60,
        "B11": 20,
        "B12": 20}


class CogNotFoundError(Exception):
    pass



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
    if not this_prod:
        raise CogNotFoundError

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


def download_s2_subset(aoi_file, date_start, date_end, out_dir, bands, conf, cloud_cover = 50, clip_to_aoi = True):
    # TODO: Add cloud cover and output EPSG as variables
    print(f"Downloading S2 subsets for {aoi_file} between {date_start} and {date_end}")
    try:
        s2_products = qry.check_for_s2_data_by_date(aoi_file,
                                                    date_start.strftime("%Y%m%d"),
                                                    date_end.strftime("%Y%m%d"),
                                                    conf,
                                                    cloud_cover)
    except KeyError as e:
        if e.args[0] == 'opensearch:totalResults':
            print("No products found.")
            return
        else:
            raise e
    print(f"{len(s2_products)} images found")

    for prod_enum, (prod_id, product) in enumerate(s2_products.items()):
        n = prod_enum +1
        print(f"Downloading product {n} of {len(s2_products)}")
        with TemporaryDirectory() as td:
            try:
                for band in bands:
                    temp_path = p.join(td, band + ".tif")
                    cog_path = build_aws_path(product, band)
                    print(f"Downloading band {band}")
                    get_subset_image(cog_path, aoi_file, temp_path, band)
                out_name = p.basename(aoi_file).rsplit('.')[0]
                out_name = out_name + '_' + str(product["beginposition"].strftime("%Y-%m-%d")) +".tif"
                out_path = p.join(out_dir, out_name)

                print(f"Stacking bands in image {n}")
                ras.stack_images([p.join(td, band + ".tif") for band in bands], p.join(td, "stacked.tif"))
                if clip_to_aoi:
                    ras.clip_raster(p.join(td, "stacked.tif"), aoi_file, out_path)
                else:
                    os.rename(p.join(td, "stacked.tif"), out_path)
                new_image = gdal.Open(out_path)
                for band_index in range(new_image.RasterCount):
                    band = new_image.GetRasterBand(band_index + 1) # Geotif bands are 1-indexed
                    band.SetDescription(bands[band_index])
                    band = None
                new_image = None
                print(f"Product {n} downloaded to {out_path}")
            except CogNotFoundError:
                print(f"Product {cog_path} not found, skipping.")
                with open("bad_cog_urls.txt", 'a') as bad_url_log:
                    bad_url_log.write(cog_path)
                    print(f"URL logged to {bad_url_log.name}")
