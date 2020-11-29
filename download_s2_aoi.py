import argparse
import configparser
from datetime import datetime as dt

from s2_cog_functions import download_s2_subset

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Downloads a subset of an S2 cloud-optimised geotif from AWS with the specified"
                                     "stacked bands. Will download any image of less than")
    parser.add_argument("aoi_file", help = "Path to a .json, .shp or .wkt file of the AOI")
    parser.add_argument("start_date", help="Start date of imagery (yyyy-mm-dd)")
    parser.add_argument("end_date", help= "End date of imagery (yyyy-mm-dd)")
    parser.add_argument("out_dir", help="Directory to contain downloaded images")
    parser.add_argument("--bands", nargs="*", default = ["B02", "B03", "B04", "B08"],
                        help="Bands to be present in the stacked image, as S2 band names. Defaults to B02, B03, B04"
                             "and B08.")
    parser.add_argument("--cred_path", default = "creds.conf", help = "Path to a config file containing Copernicus "
                                                                      "Scihub credentials. Defaults to creds.conf in"
                                                                      " the install dir of this script")
    args = parser.parse_args()

    conf = configparser.ConfigParser()
    conf.read(args.cred_path)

    start_date = dt.strptime(args.start_date, "%Y-%m-%d")
    end_date = dt.strptime(args.end_date, "%Y-%m-%d")

    # TODO: config and date parsers here
    download_s2_subset(args.aoi_file, start_date, end_date, args.out_dir, args.bands, conf)