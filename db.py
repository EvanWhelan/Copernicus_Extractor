import psycopg2 as psy
import config
import ntpath
import matplotlib.pyplot as plt
import sys
from pathlib import Path
from operator import itemgetter
from time import sleep
from decimal import Decimal
from datetime import datetime
from getpass import getpass

class DatabaseController():
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.csv_filename = None
        self.table_name = None
        self.username = config.username
        self.dbname = config.db_name
        self.password = getpass(f"PostgreSQL Password for {self.username}: ")
        self.initialise_connection()

    def set_csv_filename(self, csv_filename):
        self.csv_filename = csv_filename

    def set_table_name(self, table_name):
        self.table_name = table_name

    def initialise_connection(self):
        try:
            connection_string = "dbname='{}' user='{}' password='{}'".format(self.dbname, self.username, self.password)
            self.conn = psy.connect(connection_string)
            self.cursor = self.conn.cursor()
            print("Connection successful!")
        except Exception as e:
            print("Unable to connect to database - {}".format(e))
            quit()
    
    def create_copernicus_table(self, table_name):
        query = """
        CREATE TABLE IF NOT EXISTS {}(
            timestamp TIMESTAMP NOT NULL,
            coordinates GEOMETRY NOT NULL,
            pollutant DECIMAL NOT NULL
        );
        """.format(table_name)
        try:
            self.cursor.execute(query)
            self.conn.commit()
            print("Table Created: Name = {}".format(table_name))
        except Exception as e:
            print("Table creation failed {}".format(e))
            
    def populate_table(self, csv_file, table_exists):
        csv_file = csv_file.replace("~", f"{Path.home()}")

        if not table_exists:
            self.create_copernicus_table(self.table_name)
        
        print("Building Table")
        num_lines = self.file_len(csv_file)
        with open(csv_file) as f:        
            count = 1
            for line in f:
                percentage_complete = round((count / num_lines) * 100, 3)
                sys.stdout.write(f"Building Table - Progress: {percentage_complete}%  \r")
                sys.stdout.flush()
                query = self.build_insert_query(line)
                try:
                    self.cursor.execute(query)
                    self.conn.commit()
                    count += 1
                except Exception as e:
                    print(e)
        
        print("Finished Building Table")

    def get_closest_point_data(self, lon, lat):
        query = config.closest_point_query_template.format(self.table_name, lon, lat)
        try:
            point = self.execute_select(query)
            lon = point[0][0]
            lat = point[0][1]
            return (lon, lat)
        except Exception as e:
            print(e)
        
    def extract_data_for_point(self, lon, lat):
        query = config.all_data_for_point_query_template.format(self.table_name, lon, lat)
        try:
            data = self.execute_select(query)
            return data
        except Exception as e:
            print(e)
        
    def extract_all_data(self):
        query = config.all_data_query.format(self.table_name)
        try:
            return self.execute_select(query)
        except Exception as e:
            print(e)
            return None

    def drop_table(self):
        drop_query = config.drop_table_query_format.format(self.table_name)
        try:
            self.cursor.execute(drop_query)
            self.conn.commit()
        except Exception as e:
                print(e)
    
    def table_exists(self, specified_table_name):
        table_name = specified_table_name if specified_table_name else self.table_name
        check_table_query = config.table_exists_query_template.format(table_name)
        table_exists = self.execute_select(check_table_query)
        return table_exists[0][0] if table_exists else None
    
    def get_all_tables(self):
        query = config.all_tables_query
        return self.execute_select(query)
    
    def execute_select(self, query):
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(e)
            return None

    # extracts the file name in isolation from the rest of it's path
    def path_leaf(self, path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def generate_table_name(self, csv_filename):
        return self.path_leaf(csv_filename).replace(".csv", "")

    def file_len(self, fname):
        print("Calculating Table Size")
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    def build_insert_query(self, csv_line):            
        data = csv_line.split(',')
        timestamp = data[0]
        longitude = data[4]
        latitude = data[5]
        pollutant = float(data[6]) * config.scale_factor
        query = config.sql_query.format(self.table_name, timestamp, longitude, latitude, pollutant)
        return query.replace('"', "'")