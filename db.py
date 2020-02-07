import psycopg2 as psy
import config
import numpy as np
import pandas as pd
import ntpath
import matplotlib.pyplot as plt
from operator import itemgetter
from time import sleep
from decimal import Decimal

class DatabaseController():
    def __init__(self, grib_file_name):
        self.conn = None
        self.cursor = None
        self.csv_file_name = grib_file_name
        self.table_name = ""
        self.initialise_connection()

    def initialise_connection(self):
        try:
            db_name = config.db_name
            user_name = config.user_name
            password = self.read_password()
            connection_string = "dbname='{}' user='{}' password='{}'".format(db_name, user_name, password)
            self.conn = psy.connect(connection_string)
            self.cursor = self.conn.cursor()
            print("Connection successful!")
        except Exception as e:
            print("Unable to connect to database - {}".format(e))
    
    def create_copernicus_table(self, table_name):
        query = """
        CREATE TABLE IF NOT EXISTS {}(
            timestamp TIMESTAMP NOT NULL,
            co-ords GEOMETRY NOT NULL,
            pollutant DECIMAL NOT NULL
        );
        """.format(table_name)
        try:
            self.cursor.execute(query)
            self.conn.commit()
            print("Table Created: Name = {}".format(table_name))
        except Exception as e:
            print("Table creation failed {}".format(e))

    # this is for testing purposes, passwords will not be stored locally going forward
    def read_password(self):
        with open('/usr/local/home/u180539/Copernicus_Extractor/o/pw.txt') as f:
            return f.readline().strip()
            
    def populate_table(self, csv_file):
        with open(csv_file) as f:
            for line in f.readlines():
                query = self.build_insert_query(line)
                try:
                    self.cursor.execute(query)
                    self.conn.commit()
                except Exception as e:
                    print(e)

    def build_insert_query(self, csv_line):            
        data = csv_line.split(',')
        timestamp = data[0]
        longitude = data[4]
        latitude = data[5]
        pollutant = float(data[6]) * config.scale_factor
        query = config.sql_query.format(self.table_name, timestamp, longitude, latitude, pollutant)
        return query.replace('"', "'")
    
    def table_exists(self, table_name=None):
        table_name = table_name if table_name else self.path_leaf(self.csv_file_name).replace(".csv","")
        check_table_query = config.table_exists_query_template.format(table_name)
        self.cursor.execute(check_table_query)
        table_exists = self.cursor.fetchall()
        return table_exists[0][0]
    
    # extracts the file name in isolation from the rest of it's path
    def path_leaf(self, path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

