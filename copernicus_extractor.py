import sys
import os
import subprocess
import argparse
import config
import requests
import json
import urllib.parse
import analysis_controller
import ntpath
import errno
from getpass import getpass
from db import DatabaseController
from wgrib import WgribController
from pathlib import Path
from analysis_controller import AnalysisController
from copernicus_api import CopernicusApi

def launch():
    parser = argparse.ArgumentParser()

    parser.add_argument('-m', '--mode', required=True)
    parser.add_argument('--api', required=False, action='store_true', help="flag to toggle using the api to fetch grib files rather than downloading manually")
    parser.add_argument('-p', '--path', required=False, help="path to grib file to be processed")
    parser.add_argument('-tn', '--tablename', required=False, help='extract data from provided table name')
    parser.add_argument('-c', '--country', required=False, help='country around which to form a bounding box')
    args = parser.parse_args()

    db_controller = DatabaseController()

    mode = args.mode.lower() # mode 'a' for analysis, mode 'e' for extraction
    
    if mode == 'e':

        if not args.tablename:
            print("Usage Error: Argument --tablename required when in extract mode")
            return

        if not args.path and not args.api:  
            print("Usage Error: No path or api flag provided provided. Please provide a path to a grib2 file or include the --api flag to use the copernicus api")
            return

        if args.path and args.api:
            print("Usage Error: Please use ONLY the --api flag OR the --path argument, not both")
            return
        
        country = None
        bounding_box = None
        if args.country:
            country = args.country
            bounding_box = fetch_bounding_box(country)

        grib_files = []
        wgrib_controller = WgribController()
        
        if args.path:
            if os.path.exists(args.path):
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.path)
            
            if os.path.isfile(args.path):
                grib_file_path = args.path
                grib_files.append(grib_file_path)
            
            elif os.path.isdir:
                for file in os.listdir(args.path):
                    filename = os.fsdecode(file)
                    if filename.endswith(".grib2"):
                        grib_files.append(filename)
        elif args.api:
            api_controller = CopernicusApi()
            api_grib_files = api_controller.get_grib_data()
            grib_files.extend(api_grib_files)

        if not args.country or bounding_box is None:
            print("Warning: You have not inputted a country. This may result in csv files and databases that are multiple GB in size\n Are you sure you want to continue? [Y/n]")
            if input().lower() != "y":
                quit()
        
        tablename = args.tablename
        db_controller.set_table_name(tablename)

        if bounding_box is None and args.country:
            if input("No bounding box could be found for that country. Would you like to extract the entire file to the database? [Y/n]: ").lower() != "y":
                quit()
            
        table_exists = db_controller.table_exists(tablename)
            
        if table_exists:
            print("A table has already been created with that name")
            print("Press 1 to add this grib data to the existing database")
            print("Press 2 to delete this table and populate it with the given file")
                        
            choice = input()
            
            if choice == '2':
                db_controller.drop_table()
            elif choice == '3':
                closest_point = db_controller.get_closest_point_data(args.lon, args.lat)
                db_controller.extract_data_for_point(closest_point[0], closest_point[1])
        
        extract_data_from_grib(wgrib_controller, db_controller, grib_files, bounding_box, table_exists, country) 


    analysis_controller = AnalysisController(db_controller)
    analysis_controller.start()

def extract_data_from_grib(wgrib_controller, db_controller, grib_files, bounding_box, table_exists, country="all"):
    for grib_file in grib_files:
        
        grib_file_name = grib_file.split('.')[-2]
        small_grib_file = grib_file.replace(grib_file_name, "{}_{}".format(grib_file_name, country))
        csv_filename = create_csv_filename(grib_file)
        db_controller.set_csv_filename(csv_filename)
        
        if bounding_box:
            csv_filename = csv_filename.replace(".csv", f"_{country}.csv")
            small_grib_file = small_grib_file.replace(".grib2", f"_{country}.grib2")
            wgrib_controller.extract_bounding_box(grib_file, small_grib_file, bounding_box[0], bounding_box[1], bounding_box[2], bounding_box[3])
        
        wgrib_controller.convert_grib_to_csv(small_grib_file, csv_filename)

        db_controller.populate_table(csv_filename, table_exists)

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
            
def create_database(db_controller, csv_filename, table_exists):
    db_controller.populate_table(csv_filename, table_exists)

def create_csv_filename(grib_file):
    return grib_file.replace("+","_").replace("-","_").replace(",","_").replace(".grib2",".csv").replace("__","_")

def fetch_bounding_box(country):
    bbox_url = "http://nominatim.openstreetmap.org/search?q=%s&format=json&email=whelanevan6@gmail.com" % country.replace(" ", "+")
    headers = {
        "User-Agent": "Copernicus_Satellite_Extractor"
    }
    req = requests.get(bbox_url, headers=headers)

    if req.status_code != 200:
        print(f"Request Error: {req.status_code}")
        return 'not found'
    if has_bounding_box(req.text):
        res = json.loads(req.text)[0]["boundingbox"]
        return [float(co_ordinate) for co_ordinate in res]
    else:
        return 'not found'

# intermediate check to ensure the api can find a bounding box for inputted country
def has_bounding_box(query_result):
    if query_result == '[]' or "boundingbox" not in json.loads(query_result)[0]:
        return False
    else:
        print("Bounding Box successfully found")
        return True

if __name__ == "__main__":
    launch()