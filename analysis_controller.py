import db
import os
import sys  
import config
import csv
import matplotlib
import math
import json
import time
from matplotlib import pyplot as plt
from matplotlib import dates as md
from datetime import datetime

class AnalysisController():
    def __init__(self, db_controller):
        self.db_controller = db_controller
        self.tables = {}
        self.locations = []
        self.tablename = None
        self.data = None

    def start(self, json_path=None, table_name=None):
        self.get_all_tables()
        
        if json_path and table_name:
            self.extract_data_for_all_locations(json_path)

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

            while choice != 'reset':
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
                    
                    orignal_point = (lon, lat)
                    closest_point = self.db_controller.get_closest_point_data(lon, lat)

                    lon = closest_point[0]
                    lat = closest_point[1]
                    print(f"Closest point found: Lon={lon}, Lat={lat}")
                    self.calculate_distance(orignal_point, closest_point)
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
    

    def extract_data_for_all_locations(self, json_path):

        # makes a directory in the project's folder that contains verification data for the supplied locations
        dir_name = config.verification_dir_name_template.format(int(time.time()))
        try:
            os.mkdir(dir_name, 0o755)
        except OSError as e:
            print(e)
        
        with open(json_path) as json_file:
            data = json.load(json_file)
            self.locations.extend(data["stations"])

        core_pollutants = config.core_pollutants

        for location in self.locations:
            station = location["placename"]
            lon = float(location["longitude"])
            lat = float(location["latitude"])
            closest_point = self.db_controller.get_closest_point_data(lon, lat)
            csv_filename = f"{dir_name}/{station}_{lat}_{lon}.csv"

            for pollutant in core_pollutants:
                self.data = self.db_controller.extract_data_for_point(closest_point[0], closest_point[1], pollutant)
                self.write_data_to_csv(csv_filename, ignore_existing_file=True)

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

    def write_data_to_csv(self, csv_path, ignore_existing_file=None):
        if self.data is None:
            print("No data to extract")
            return

        line_count = len(self.data)
        count = 1

        if os.path.exists(csv_path) and not ignore_existing_file:
            choice = input("\nA csv file already exists at that location. Do you want to overwrite it with this data? [Y/n]")
            overwrite = choice.lower() == "y"
            if overwrite:
                open(csv_path, 'w').close() # this erases all data from the file without having to delete it
            else:
                csv_path = input("\nPlease enter another path: ")

        # the reason for 2 opens is to allow the first to write the header row if necessary
        has_header = False
        with open(csv_path, 'r') as f:
            sniffer = csv.Sniffer()
            has_header = sniffer.has_header(f.read(2048))
        
        with open(csv_path, 'a', newline='') as f:
            writer = csv.writer(f)

            if not has_header:
                writer.writerow(config.csv_header_row)                
            
            for line in self.data:
                percentage_complete = round((count / line_count) * 100, 3)
                sys.stdout.write(f"Writing to CSV - Progress: {percentage_complete}%  \r")
                sys.stdout.flush()
                timestamp = line[0]
                lon = line[1]
                lat = line[2]
                pollutant = line[3]
                pollutant_name = line[4]
                csv_row = [timestamp, lon, lat, pollutant, pollutant_name]
                writer.writerow(csv_row)
                count += 1
        
        print("\nFinished writing to csv")
    
    def extract_time_series(self):
        times = []
        polls = []

        for row in self.data:
            time = datetime.strftime(row[0], "%Y-%m-%d %H:%M:%S")
            poll = float(row[3])
            times.append(time)
            polls.append(poll)
            print(f"{time} - {poll}")
            
        print(len(times), len(polls))
        plt.plot(times, polls, '--bo')
        plt.xticks(rotation=90)
        plt.grid()  
        plt.title("Time Series of Pollutant Value")
        plt.xlabel("Timestamp")
        plt.ylabel("Pollutant Value")
        plt.show()

    def calculate_mean(self):
        pollutants = []
        for line in self.data:
            pollutants.append(line[2])

        return 0 if len(pollutants) == 0 else sum(pollutants) / len(pollutants)

    def calculate_distance(self, original_point, closest_point):
        # Implementation of the Haversine formula to calculate distance between two points
        R = 6373.0
        
        lon1 = math.radians(float(original_point[0]))
        lat1 = math.radians(float(original_point[1]))
        lon2 = math.radians(float(closest_point[0]))
        lat2 = math.radians(float(closest_point[1]))

        dlon = lon2 - lon1

        dlat = lat2 - lat1

        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        print(f"The closest point found is {round(distance,3)} km from your inputted point")