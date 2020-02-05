import sys
import os
import subprocess
import argparse
from db import DatabaseController
from wgrib import WgribController
from pathlib import Path

def launch():

    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--path', required=False, help="path to grib file to be processed")
    parser.add_argument('-tn', '--tablename', dest='table_name' , required=False, help='extract data from provided table name')
    args = parser.parse_args()

    grib_file_path = args.path
    grib_file_name = grib_file_path.split('.')[-2]
    csv_output_file = grib_file_path.replace("grib2", "csv")
    small_grib_file = grib_file_path.replace(grib_file_name, "{}_small".format(grib_file_name))
    db_controller = DatabaseController(csv_output_file)
    wgrib_controller = WgribController()
    
    if args.path and args.table_name:
        print("Please specify a path OR a table name (not both)")
        quit()

    table_exists = db_controller.table_exists(args.table_name) if args.table_name else db_controller.table_exists()
        
    if table_exists and args.path:
        print("A table has already been created with that grib file")
        print("Press 1 to continue with the existing table")
        print("Press 2 to Enter Your Co-Ordinates")
        
        choice = input()
        
        quit()
        
        if input("A table for that grib file already exists.\nWould you like to override it with this file? [Y/n]").lower() == "y":
            extract_data_from_lat_lon()
            convert_to_csv()
            create_database()
        else:
            print("Extracting..")
    else:
        #TODO - Extract data from existing database based on latitude / longitude
        print("")

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

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
