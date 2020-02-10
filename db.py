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
    def __init__(self, csv_filename, username, password, dbname, tablename=None):
        self.conn = None
        self.cursor = None
        self.csv_filename = csv_filename
        self.username = username
        self.password = password
        self.dbname = dbname
        self.table_name = tablename if tablename else self.generate_table_name(self.csv_filename)
        self.initialise_connection()

    def initialise_connection(self):
        try:
            connection_string = "dbname='{}' user='{}' password='{}'".format(self.dbname, self.username, self.password)
            self.conn = psy.connect(connection_string)
            self.cursor = self.conn.cursor()
            print("Connection successful!")
        except Exception as e:
            print("Unable to connect to database - {}".format(e))
    
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
        if not table_exists:
            self.create_copernicus_table(self.table_name)
        
        print("Building Table")
        num_lines = self.file_len(csv_file)
        with open(csv_file) as f:        
            count = 1
            for line in f:
                percentage_complete = round((count / num_lines) * 100, 3)
                sys.stdout.write("Building Table - Progress: %d%%   \r" % (percentage_complete) )
                sys.stdout.flush()
                query = self.build_insert_query(line)
                try:
                    self.cursor.execute(query)
                    self.conn.commit()
                    count += 1
                except Exception as e:
                    print(e)
        
        print("Finished Building Table")
    
    def drop_table(self):
        drop_query = f"DROP TABLE IF EXISTS {self.table_name};"
        try:
            self.cursor.execute(drop_query)
            self.conn.commit()
            self.table_exists = False
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
    
    def table_exists(self, specified_table_name):
        table_name = specified_table_name if specified_table_name else self.table_name
        check_table_query = config.table_exists_query_template.format(table_name)
        self.cursor.execute(check_table_query)
        table_exists = self.cursor.fetchall()
        return table_exists[0][0]
    
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