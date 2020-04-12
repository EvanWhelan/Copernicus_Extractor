import db
import os
import sys  
import config
import csv
import matplotlib
import math
import json
import time
import mplcursors
import pandas as pd
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
        
        self.present_user_menus()

    def present_user_menus(self):
        while True:
            self.print_database_options()
            choice = input("Choice: ").lower()
            if choice == 'q':
                quit()
            elif choice == 'reset':
                self.present_user_menus()
            elif choice == '1':
                self.print_table_options()
                selected_table = input("\nSelect which table you want to query: ")
                if selected_table == 'q':
                    quit()
                elif selected_table == 'reset':
                    self.present_user_menus()
                
                table_choice = ""
                valid_input = False

                while not valid_input:
                    try:
                        table_choice = int(input("Enter an integer value to choose from the displayed tables: "))
                        
                        if table_choice > len(self.tables):
                            continue

                        valid_input = True
                    except Exception as e:
                        continue

                self.tablename = self.tables[int(table_choice)]
            elif choice == '2':
                self.tablename = input("\nTable Name: ")
                while not self.db_controller.table_exists(self.tablename):
                    tablename = input("\nTable doesn't exist. Please enter another table name :")
                    if tablename == 'q':
                        quit()
                    elif tablename == 'reset':
                        self.present_user_menus()

            self.db_controller.set_table_name(self.tablename)

            while choice != 'reset':
                self.print_location_options()

                choice = input("\nChoice: ").lower()
                use_own_location = False
                if choice == 'q':
                    quit()
                elif choice == 'reset':
                    self.present_user_menus()
                elif choice == '1':
                    co_ordinates = input("\nInput lon/lat in form (lon, lat): ").replace("(","").replace(")","").replace(" ", "").split(",")
                    print(co_ordinates)
                    if co_ordinates[0] == 'q':
                        quit()
                    elif co_ordinates[0] == 'reset':
                        self.present_user_menus()
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

                if analysis_option == 'q':
                    quit()
                elif analysis_option == 'reset':
                    continue
                elif analysis_option == '1':
                    csv_path = input("\nPlease Enter An Absolute File Path: ")
                    if csv_path == 'q':
                        quit()
                    elif csv_path == 'reset':
                        continue
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

    def write_data_to_csv(self, csv_path, ignore_existing_file=None):
        if self.data is None:
            print("No data to extract")
            return

        line_count = len(self.data)
        count = 1

        file_exists = os.path.exists(csv_path)

        if not file_exists:
            with open(csv_path, 'x'):
                print("Created new CSV file")

        if file_exists and not ignore_existing_file:
            choice = input("\n csv file already exists at that location. Do you want to overwrite it with this data? [Y/n]")

            if choice == 'q':
                quit()
            elif choice == 'reset':
                self.present_user_menus()
                return

            overwrite = choice.lower() == "y"
            if overwrite:
                open(csv_path, 'w').close() # this erases all data from the file without having to delete it
            else:
                csv_path = input("\nPlease enter another path: ")

                if csv_path == 'q':
                    quit()
                elif csv_path == 'reset':
                    self.present_user_menus()
                    return 

        file_is_empty = os.stat(csv_path).st_size == 0
        
        with open(csv_path, 'a', newline='') as f:
            writer = csv.writer(f)

            if file_is_empty:
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
        
        pollutant_name = self.db_controller.get_pollutant_name()

        start_date = min(item[0] for item in self.data)
        end_date = max(item[0] for item in self.data)

        formatted_start_date = datetime.strftime(start_date, "%b %d %Y")
        formatted_end_date = datetime.strftime(end_date, "%b %d %Y")

        for row in self.data:
            time = row[0]
            poll = float(row[3])
            times.append(time)
            polls.append(poll)
            print(f"{time} - {poll}")

        co_ordinate = (self.data[0][1], self.data[0][2])
        
        fig, ax = plt.subplots()
        ax.plot_date(times, polls, "--bo")

        plt.xticks(rotation=60)
        plt.xlabel("Timestamp")
        plt.ylabel("Pollutant Value")

        graph_title = f"{pollutant_name} Values For {formatted_start_date} to {formatted_end_date} For (lat, lon) = ({co_ordinate[0]},{co_ordinate[1]})"
        
        plt.tight_layout(h_pad=1.08)
        plt.show()
        plt.savefig(f"{graph_title.replace(' ', '_')}.png")

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