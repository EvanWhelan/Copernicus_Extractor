import db
import os
import sys  
import config
import datetime
import csv
import matplotlib
# this process finds appropriate back ends for matplotlib
gui_env = ['TKAgg','GTKAgg','Qt4Agg','WXAgg']
for gui in gui_env:
    try:
        matplotlib.use(gui,warn=False, force=True)
        break
    except:
        continue

from matplotlib import pyplot as plt
from matplotlib import dates as md

class AnalysisController():
    def __init__(self, db_controller):
        self.db_controller = db_controller
        self.tables = {}
        self.get_all_tables()
        self.tablename = None
        self.data = None

    def start(self):
        while True:
            self.print_database_options()
            choice = input().lower()
            if choice == 'q':
                quit()
            elif choice == 'reset':
                continue
            elif choice == '1':
                self.print_table_options()
                self.tablename = self.tables[int(input("\nSelect which table you want to query: "))]
            elif choice == '2':
                self.tablename = input("\nTable Name: ")
                while not self.db_controller.table_exists(self.tablename):
                    self.tablename = input("\nTable doesn't exist. Please enter another table name :")
            
            self.db_controller.set_table_name(self.tablename)

            self.print_location_options()

            choice = input("\nChoice: ").lower()
            use_own_location = False
            if choice == 'q':
                quit()
            elif choice == 'reset':
                continue
            elif choice == '1':
                co_ordinates = input("\nInput lon/lat in form (lon, lat): ").replace("(","").replace(")","").replace(" ", "").split(",")

                if co_ordinates == 'q':
                    quit()
                elif co_ordinates == 'reset':
                    continue
                use_own_location = True

                lon = co_ordinates[0]
                lat = co_ordinates[1]
                
                closest_point = self.db_controller.get_closest_point_data(lon, lat)

                lon = closest_point[0]
                lat = closest_point[1]

                self.data = self.db_controller.extract_data_for_point(lon, lat)
            elif choice == '2':
                self.data = self.db_controller.extract_all_data()
        
            self.print_analysis_options(use_own_location)

            analysis_option = input("\nChoice: ")

            if choice == 'q':
                quit()
            elif choice == 'reset':
                continue
            if analysis_option == '1':
                csv_path = input("\nPlease Enter An Absolute File Path: ")
                self.write_data_to_csv(csv_path)
            elif analysis_option == '2':
                mean = self.calculate_mean()
                print(f"Mean value for pollutant = {mean}")
            elif analysis_option == '3' and use_own_location:
                self.extract_time_series()
        
    def get_all_tables(self):
        tables = self.db_controller.get_all_tables()
        for i, table in enumerate(tables):
            self.tables[i+1] = table[0]
        
    def print_analysis_options(self, use_own_location):
        print("\nPress 1 to extract data to csv")
        print("Press 2 to calculate the mean value for the pollutant")
        if use_own_location:
            print("Press 3 to extract a time series for your given point")

    def print_location_options(self):
        option1 = "Press 1 to input your location (lon, lat)"
        option2 = "Press 2 to query all data in the table"
        print(f"\n{option1}\n{option2}")

    def print_table_options(self):
        for key in self.tables:
            print(f"\n{key}) {self.tables[key]}")

    def print_database_options(self):
        print("\nPress 1 to list all tables in database")
        print("Press 2 to manually enter a table name")
        print("Type 'reset' at any time to change table")
        print("Type 'q' at any time to quit")

    def write_data_to_csv(self, csv_path):
        if self.data is None:
            print("No data to extract")
            return

        line_count = len(self.data)
        count = 1

        if os.path.exists(csv_path):
            choice = input("\nA csv file already exists at that location. Do you want to overwrite it with this data? [Y/n]")
            overwrite = choice.lower() == "y"
            if overwrite:
                open(csv_path, 'w').close() # this erases all data from the file without having to delete it
            else:
                csv_path = input("\nPlease enter another path: ")
        
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(config.csv_header_row)
            for line in self.data:
                percentage_complete = round((count / line_count) * 100, 3)
                sys.stdout.write(f"Writing to CSV - Progress: {percentage_complete}%  \r")
                sys.stdout.flush()
                timestamp = line[0]
                point = line[1].replace("POINT", "").replace(" ", ",")
                pollutant = line[2]
                csv_row = [timestamp, point, pollutant]
                writer.writerow(csv_row)
                count += 1
        
        print("\nFinished writing to csv")
    
    def extract_time_series(self):
        timestamps = []
        pollutants = []

        for line in self.data:
            timestamps.append(line[0])
            pollutants.append(float(line[2]))

        plt.xticks(rotation=25)
        plt.plot(timestamps, pollutants)
        plt.title("Timeseries of Selected Pollutant")
        plt.xlabel("Timestamp")
        plt.ylabel("Pollutant Value")
        plt.show()        

    def calculate_mean(self):
        pollutants = []
        for line in self.data:
            pollutants.append(line[2])

        return 0 if len(pollutants) == 0 else sum(pollutants) / len(pollutants)