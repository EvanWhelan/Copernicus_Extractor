import sys
import os
import subprocess
from db import DatabaseController

def launch():
    new_data_flag = True if sys.argv[1] == 't' else False
    grib_file_path = sys.argv[2]
    grib_file_name = grib_file_path.split('.')[-2]
    csv_output_file = grib_file_path.replace("grib2", "csv")
    small_grib_file = grib_file_path.replace(grib_file_name, "{}_small".format(grib_file_name))
    db = DatabaseController(csv_output_file, new_data_flag)
    
    if new_data_flag:
        extract_data_from_lat_lon()
        convert_to_csv()
        create_database()
    else:
        #TODO - Extract data from existing database based on latitude / longitude

def extract_data_from_lat_lon():
    wgrib2_small_grib_command = "wgrib2 {} -small_grib -12.316:-4.98 51.43:55.36 {}".format(grib_file_path, small_grib_file)
    print "Extracting data for specified lat/lon"
    process = subprocess.Popen(wgrib2_small_grib_command, shell=True)
    process.wait()
    print "Finished extracting data. Status code {}".format(process.returncode)
    
def convert_to_csv():
    wgrib2_csv_command = "wgrib2 {} -csv {}".format(small_grib_file, csv_output_file)
    print "Converting data to csv"
    process = subprocess.Popen(wgrib2_csv_command, shell=True)
    process.wait()
    print "Finished converting data to csv. Status code {}".format(process.returncode)

def create_database():
    global db
    db.populate_table(csv_output_file)

if __name__ == "__main__":
    launch()