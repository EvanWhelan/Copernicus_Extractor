import db
import os
import sys
from time import strftime

class AnalysisController():
    def __init__(self, db_controller):
        self.db_controller = db_controller
        self.tables = {}
        self.get_all_tables()
        self.table_name = None

    def start(self):

        print("Press 1 to list all tables in database")
        print("Press 2 to manually enter a table name")

        choice = input()

        if choice == '1':
            print("Select which table you want to query: ") 
            self.print_table_options()
            self.table_name = self.tables[int(input())]
        elif choice == '2':
            self.table_name = input("Table Name: ")
            while not self.db_controller.table_exists(tablename):
                self.table_name = input("Table doesn't exist. Please enter another table name :")
                
        self.db_controller.set_table_name(self.table_name)

        self.print_location_options()

        location_choice = input("Choice: ")

        if location_choice == '1':
            co_ordinates = input("Input lon/lat in form (lon, lat): ").replace("(","").replace(")","").replace(" ", "").split(",")
            
            lon = co_ordinates[0]
            lat = co_ordinates[1]
            
            closest_point = self.db_controller.get_closest_point_data(lon, lat)

            lon = closest_point[0]
            lat = closest_point[1]

            data = self.db_controller.extract_data_for_point(lon, lat)
        elif location_choice == '2':
            data = self.db_controller.extract_all_data()
    
        use_own_location = location_choice == '1'
        self.print_analysis_options(use_own_location)

        analysis_option = input("Choice: ")

        if analysis_option == '1':
            csv_path = input("Please Enter An Absolute File Path: ")
            self.write_data_to_csv(data, csv_path)
        
    def get_all_tables(self):
        tables = self.db_controller.get_all_tables()
        for i, table in enumerate(tables):
            self.tables[i+1] = table[0]
        
    def print_analysis_options(self, use_own_location):
        print("Press 1 to extract data to csv")
        print("Press 2 to calculate the mean value for the pollutant")
        if use_own_location:
            print("Press 3 to extract a time series for your given point")

    def print_location_options(self):
        option1 = "Press 1 to input your location (lon, lat)"
        option2 = "Press 2 to query all data in the table"
        print(f"{option1}\n{option2}")

    def print_table_options(self):
        for key in self.tables:
            print(f"{key}) {self.tables[key]}")

    def write_data_to_csv(self, data, csv_path):
        line_count = len(data)
        count = 1

        if os.path.exists(csv_path):
            overwrite = input("A file already exists at that path. Overwrite? [Y/n]")
            if overwrite:
                open(csv_path, 'w').close() # this erases all data from the file without deleting it
        
        with open(csv_path, 'w') as f:
            f.write(config.csv_header)
            for line in data:
                percentage_complete = round((count / line_count) * 100, 3)
                sys.stdout.write(f"Writing to CSV - Progress: {percentage_complete}%  \r")
                sys.stdout.flush()
                timestamp = line[0][0]
                point = line[1][0].replace("Point(", "").replace(")", "")
                pollutant = line[2][0]
                csv_line = f"{timestamp},{point},{pollutant}\n"
                count += 1
                f.write(csv_line)
    
    def extract_time_series(self, data):
        #TODO - Extract Time Series
        pass

    def calculate_mean(self, data):
        #TODO - Calculate mean value of pollutant across entire data
        pass