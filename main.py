import sys
import os
import subprocess
from db import DatabaseController
from wgrib import WgribController
from pathlib import Path

# required args: (-[d/F] , <filepath>)
def launch():
    if len(sys.argv) != 3:
        print("Please enter args in the following order: -[d/F] <file_path>")
        return
    else:
        print("Correct")
    
    quit()
    use_single_file = sys.argv[1] == '-F'
    grib_path = sys.argv[2]
    grib_file_name = grib_file_path.split('.')[-2]
    csv_output_file = grib_file_path.replace("grib2", "csv")
    small_grib_file = grib_file_path.replace(grib_file_name, "{}_small".format(grib_file_name))
    db_controller = DatabaseController(csv_output_file)
    wgrib_controller = WgribController()
    
    will_create_table = db_controller.table_exists()
    if will_create_table:
        if raw_input("A table for that grib file already exists.\nWould you like to override it with this file? [Y/n]").lower() == "y":
            extract_data_from_lat_lon()
            convert_to_csv()
            create_database()
        else:
            print("Extracting..")
        quit()
    else:
        #TODO - Extract data from existing database based on latitude / longitude
        print("")

def extract_data_from_all_files(directory):
    for pth in Path.cwd().iterdir():
        if pth.suffix.includes('grib'):
            output_file_name = pth.split('/')[-1].replace(pth.suffix, '')
            print(output_file_name)
        
def extract_data_from_lat_lon(input_grib_file, output_grib_file):
    wgrib2_small_grib_command = "wgrib2 {} -small_grib -12.316:-4.98 51.43:55.36 {}".format(input_grib_file, output_grib_file)
    print("Extracting data for specified lat/lon")
    process = subprocess.Popen(wgrib2_small_grib_command, shell=True)
    process.wait()
    print("Finished extracting data. Status code {}".format(process.returncode))
    
def convert_to_csv():
    wgrib2_csv_command = "wgrib2 {} -csv {}".format(small_grib_file, csv_output_file)
    print("Converting data to csv")
    process = subprocess.Popen(wgrib2_csv_command, shell=True)
    process.wait()
    print("Finished converting data to csv. Status code {}".format(process.returncode))

def create_database():
    global db_controller    
    db_controller.populate_table(csv_output_file)

if __name__ == "__main__":
    launch()
