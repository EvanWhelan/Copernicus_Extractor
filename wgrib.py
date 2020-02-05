import os
import subprocess

class WgribController:
    # Params: left = latitude of left side of bounding box
    # Params: right = latitude of right side of bounding box
    # Params: top = longitude of top of bounding box
    # Params: bottom = longitude of bottom of bounding box   
    def extract_bounding_box(self, grib_file_path, small_grib_file,  left, right, bottom, top):
        wgrib2_small_grib_command = "wgrib2 {} -small_grib {}:{} {}:{} {}".format(grib_file_path, left, right, bottom, top, small_grib_file)
        print("Extracting data for given bounding box")
        self.wgrib_execute(wgrib2_small_grib_command)
        print("Finished extracting data for given bounding box")

    def convert_grib_to_csv(self, grib_path, out_path):
        wgrib2_csv_command = "wgrib2 {} -csv {}".format(grib_path, out_path)
        print("Generating csv file")
        self.wgrib_execute(wgrib2_csv_command)
        print("Finished generating csv")

    def wgrib_execute(self, wgrib_command):
        process = subprocess.Popen(wgrib_command, shell=True)
        process.wait()