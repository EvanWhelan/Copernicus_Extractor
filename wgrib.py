import os
import subprocess
from pathlib import Path

class WgribController:
    # Params: left = latitude of left side of bounding box
    # Params: right = latitude of right side of bounding box
    # Params: top = longitude of top of bounding box
    # Params: bottom = longitude of bottom of bounding box   
    def extract_bounding_box(self, grib_file_path, small_grib_file,  left, right, bottom, top):
        small_grib_file = small_grib_file.replace("~/", f"{Path.home()}")
        if os.path.exists(small_grib_file):
            print("File already generated for this bounding box")
            return

        wgrib2_small_grib_command = "wgrib2 {} -small_grib {}:{} {}:{} {}".format(grib_file_path, left, right, bottom, top, small_grib_file)
        print("Extracting data for given bounding box")
        self.wgrib_execute(wgrib2_small_grib_command)
        print("Finished extracting data for given bounding box")

    def convert_grib_to_csv(self, grib_path, csv_filename):
        csv_filename = csv_filename.replace("~", f"{Path.home()}")
        if os.path.exists(csv_filename):
            print("Csv file arlready generated for this bounding box")
            return

        wgrib2_csv_command = "wgrib2 {} -csv {}".format(grib_path, csv_filename)
        print("Generating csv file")
        self.wgrib_execute(wgrib2_csv_command)
        print("Finished generating csv")

    def wgrib_execute(self, wgrib_command):
        process = subprocess.run(wgrib_command, shell=True)