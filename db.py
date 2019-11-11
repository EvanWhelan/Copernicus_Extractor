import psycopg2 as psy
import config
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from operator import itemgetter
from time import sleep
from decimal import Decimal

class DatabaseController():
    def __init__(self, grib_file_name, create_table_flag):
        self.conn = None
        self.cursor = None
        self.csv_file_name = grib_file_name
        self.table_name = ""
        self.initialise_connection(create_table_flag)

    def initialise_connection(self, create_table_flag):
        try:
            db_name = config.db_name
            user_name = config.user_name
            password = "<password_here>"
            connection_string = "dbname='{}' user='{}' password='{}'".format(db_name, user_name, password)
            self.conn = psy.connect(connection_string)
            self.cursor = self.conn.cursor()
            print("Connection successful!")
            if create_table_flag:
                self.create_copernicus_table()
        except Exception as e:
            print("Unable to connect to database - {}".format(e))
    
    # This ensures there will always be a table in which the data can be stored
    def create_copernicus_table(self):
        self.table_name = "copernicus_data_{}".format(self.csv_file_name.split('.csv')[-2].split('/')[-1])
        query = """
        CREATE TABLE IF NOT EXISTS {}(
            timestamp TIMESTAMP NOT NULL,
            longitude DECIMAL NOT NULL,
            latitude DECIMAL NOT NULL,
            pollutant DECIMAL NOT NULL
        );
        """.format(self.table_name)
        try:
            self.cursor.execute(query)
            self.conn.commit()
            print("Table Created: Name = {}".format(table_name))
        except Exception as e:
            print("Table creation failed {}".format(e))

    def read_password(self):
        with open('/usr/local/home/u180539/Final-Year-Project/o/pw.txt') as f:
            return f.readline().strip()
            
    def populate_table(self, csv_file):
        with open(csv_file) as f:
            for line in f.readlines():
                query = self.build_query(line)
                try:
                    self.cursor.execute(query)
                    self.conn.commit()
                except Exception as e:
                    print e

    def build_query(self, csv_line):            
        data = csv_line.split(',')
        timestamp = data[0]
        longitude = data[4]
        latitude = data[5]
        pollutant = float(data[6]) * config.scale_factor
        query = config.sql_query.format(self.table_name, timestamp, longitude, latitude, pollutant)
        return query.replace('"', "'")

