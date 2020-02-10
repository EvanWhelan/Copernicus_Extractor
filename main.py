import sys
import os
import subprocess
import argparse
import config
import requests
import json
import urllib.parse
from getpass import getpass
from db import DatabaseController
from wgrib import WgribController
from pathlib import Path

def launch():
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--path', required=False, help="path to grib file to be processed")
    parser.add_argument('-tn', '--tablename', required=False, help='extract data from provided table name')
    parser.add_argument('-c', '--country', required=False, help='country around which to form a bounding box')
    args = parser.parse_args()
    
    bounding_box = fetch_bounding_box(args.country) if args.country else None
    tablename = args.tablename if args.tablename else None

    if bounding_box is None and args.country:
        print("No bounding box could be found for that country. Would you like to extract the entire file to the database? [Y/n]")
        if input().lower() != "y":
            quit()
        
    if args.path and not args.country or bounding_box is None:
        print("Warning: You have not inputted a country. This may result in csv files and databases that are multiple GB in size\n Are you sure you want to continue? [Y/n]")
        if input().lower() != "y":
            quit()

    grib_file_path = args.path if args.path else None
    
    grib_file_name = grib_file_path.split('.')[-2]
    csv_filename = create_csv_filename(grib_file_path)
    small_grib_file = grib_file_path.replace(grib_file_name, "{}_small".format(grib_file_name))
    
    if bounding_box:
        csv_filename = csv_filename.replace(".csv", f"_{bounding_box[0]}_{bounding_box[1]}_{bounding_box[2]}_{bounding_box[3]}.csv")
        small_grib_file = small_grib_file.replace(".grib2", f"_{bounding_box[0]}_{bounding_box[1]}_{bounding_box[2]}_{bounding_box[3]}.grib2")
    
    dbname = config.db_name
    username = config.username
    password = getpass(f"PostgreSQL Password for {username}: ")

    db_controller = DatabaseController(csv_filename, username, password, dbname, tablename)
    wgrib_controller = WgribController()
    
    table_exists = db_controller.table_exists(args.tablename)
        
    if table_exists:
        print("A table has already been created with that name")
        print("Press 1 to add grib data to this database")
        print("Press 2 to delete this table and populate it with the given file")
        
        
        choice = input()
        
        if choice == '2':
            db_controller.drop_table()
                
    extract_data_from_grib(wgrib_controller, grib_file_path, small_grib_file, csv_filename, bounding_box) 
    create_database(db_controller, csv_filename, table_exists)       

def extract_data_from_grib(wgrib_controller, grib_file, small_grib_file, csv_filename, bounding_box):
    if bounding_box:
        wgrib_controller.extract_bounding_box(grib_file, small_grib_file, bounding_box[0], bounding_box[1], bounding_box[2], bounding_box[3])
    
    wgrib_controller.convert_grib_to_csv(small_grib_file, csv_filename)
    
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
            
def create_database(db_controller, csv_filename, table_exists):
    db_controller.populate_table(csv_filename, table_exists)

def create_csv_filename(grib_file):
    return grib_file.replace("+","_").replace("-","_").replace(",","_").replace(".grib2",".csv").replace("__","_")

def fetch_bounding_box(country):
    print("Getting bounding box...")
    bbox_url = "http://nominatim.openstreetmap.org/search?q=%s&format=json" % country.replace(" ", "+")
    req = requests.get(bbox_url)
    return  [float(co_ordinate) for co_ordinate in json.loads(req.text)[0]["boundingbox"]] if has_bounding_box(req.text) else 'not_found'

# intermediate check to ensure the api can find a bounding box for inputted country
def has_bounding_box(query_result):
    if query_result == '[]' or "boundingbox" not in json.loads(query_result)[0]:
        return False
    else:
        print("Bounding Box successfully found")
        return True
    
if __name__ == "__main__":
    launch()
