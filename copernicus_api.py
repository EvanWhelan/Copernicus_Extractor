import requests
import os
import config
import config
import time
from datetime import date, timedelta, datetime
from wgrib import WgribController

class CopernicusApi:
    def __init__(self):
        self.token = config.token
        self.species_options = config.copernicus_species
        self.species = None
        self.start_date = None
        self.end_date = None
        self.dates = []
        self.dir_name = config.copernicus_dir_name.format(int(time.time()))
        self.get_user_options()
        self.make_grib_directory()
        self.grib_file_paths = []

    def get_grib_data(self):
        model = "ENSEMBLE"

        for date in self.dates:
            reference_time = datetime.strftime(date, "%Y-%m-%dT%H:%M:%S%z")
            formatted_reference_time = f"{reference_time}Z"
            url = config.copernics_url_format.format(self.token, self.species, formatted_reference_time)
            req = requests.get(url)
            file_path = f"{self.dir_name}/{config.copernicus_api_file_format.format(model, self.species, formatted_reference_time)}"
            self.grib_file_paths.append(file_path)
            with open(file_path, 'wb') as f:
                f.write(req.content)

        return self.grib_file_paths

    # this creates a directory in which all files will be stored that are fetched via the API
    def make_grib_directory(self): 
        try:
            os.mkdir(self.dir_name, 0o755)
        except OSError as e:
            print(e)
            
    def get_user_options(self):
        if config.token == '':
            print("Error: Please provide a valid API token to the config.py file")
            quit()
        
        print("Select Species: ")

        for key in self.species_options:
            print(f"({key}) {self.species_options[key]}")

        choice = input("Choice : ")
        while not type(choice) is int and not int(choice) in self.species_options:
            choice = input("Please enter an integer value corresponding to the options above: ")

        self.species = self.species_options[int(choice)]

        start_date = input("Enter your start date in plain text (Example format: Jan 12 2019) :")
        self.start_date = datetime.strptime(start_date, '%b %d %Y')

        end_date = input("Enter end date : ")
        self.end_date = datetime.strptime(end_date, '%b %d %Y')

        self.generate_date_range()

    def generate_date_range(self):
        if self.end_date is None:
            self.dates.append(self.start_date)
        else:
            delta = self.end_date - self.start_date
            for i in range(delta.days + 1):
                date = self.start_date + timedelta(days = i)
                print(date)
                self.dates.append(date)