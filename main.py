import sys
import os
import subprocess
import argparse
import config
import requests
import json
from db import DatabaseController
from wgrib import WgribController
from pathlib import Path

def launch():
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--path', required=False, help="path to grib file to be processed")
    parser.add_argument('-tn', '--tablename', dest='table_name' , required=False, help='extract data from provided table name')
    parser.add_argument('-c', '--country', required=False, help='country around which to form a bounding box')
    args = parser.parse_args()

    grib_file_path = args.path
    grib_file_name = grib_file_path.split('.')[-2]
    csv_output_file = create_csv_filename(grib_file_path)
    small_grib_file = grib_file_path.replace(grib_file_name, "{}_small".format(grib_file_name))
    
    db_controller = DatabaseController(csv_output_file)
    wgrib_controller = WgribController()
    
    if args.path and args.table_name:
        print("Please specify a path OR a table name (not both)")
        quit()

    table_exists = db_controller.table_exists(args.table_name) if args.table_name else db_controller.table_exists()
        
    if table_exists:
        print("A table has already been created with that grib file")
        print("Press 1 to continue with the existing table")
        print("Press 2 to Enter Your Co-Ordinates")
        
        choice = input()
        
        if input("A table for that grib file already exists.\nWould you like to override it with this file? [Y/n]").lower() == "y":
            extract_data_from_grib(wgrib_controller, grib_file_path, small_grib_file, csv_output_file)
            create_database(db_controller, csv_output_file)
        else:
            print("Extracting..")
    else:
        extract_data_from_grib(wgrib_controller, grib_file_path, small_grib_file, csv_output_file) 
        create_database(db_controller, csv_output_file, table_exists)       

def extract_data_from_grib(wgrib_controller, grib_file, small_grib_file, csv_filename, bounding_box=None):
    box = config.ireland_bounding_box
    wgrib_controller.extract_bounding_box(grib_file, small_grib_file, box[0], box[1], box[2], box[3])
    wgrib_controller.convert_grib_to_csv(small_grib_file, csv_filename)
    
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
            
def create_database(db_controller, csv_filename, table_exists):
    db_controller.populate_table(csv_filename, table_exists)

def create_csv_filename(grib_file):
    return grib_file.replace("+","_").replace("-","_").replace(",","_").replace(".grib2",".csv").replace("__","_")

def fetch_bounding_box(country):
    req = requests.get("http://nomitam.openstreetmap.org/search?q=%s&format=json".format(country))
    return json.loads(req.text)[0]["boundingbox"]
    
if __name__ == "__main__":
    launch()
