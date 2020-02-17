# Copernicus_Extractor
Copernicus_Extractor is my final year project as part of my Computer Science & Software Engineering Degree (Maynooth University).

## Purpose  
This tool can be used to extract air quality data published by the Copernicus Satellite.

The tool leverages the __wgrib2__ tool to help extract data from the grib file published by the satellite.

### Dependencies

* Python version >= 3.6
#### Python Packages
* psycopg2
* urllib 
* matplotlib

## Usage
The entry point to the software is copernicus_extractor.py.

It can be run in two modes: Extract Mode & Analyse Mode

Use the `--mode` argument to toggle between modes. (Pass 'A' for analyse and 'E' for extract)

##### Database Connection

Modify the `username` and `db_name` variables found in `config.py` to match your own database details.

The user will be prompted for password via the command line when the app is run.

#### Extract Mode

Extract mode is used to extract data from grib file and store it in a PostgreSQL Database for further use.
You can specify a country by which you want to filter the data

##### Supplying a grib2 file

You must supply a path to the grib2 file by using the `--path` argument

Example:

`python3.7 copernicus_extractor.py --mode E --path ~/data/example1.grib2`

This will extract data from the file found in the data folder in the user's home directory

##### Specifying a country by which to filter the data

Use the `--country` flag, followed by the country's name.

Example:

`python3.7 copernicus_extractor.py --mode e --country Ireland`

This will extract all air quality data within a bounding box that surrounds Ireland.

The bounding box is retrieved by using the [Nominatim OpenStreetMap API](https://wiki.openstreetmap.org/wiki/Nominatim)

***NOTE : If a country is not specified, the entire dataset will be stored in the database, which may be upwards of 1GB in size depending on the file you use***

##### Specifying a table name

You can specify the name of the table you want the data to be stored in with the `--tablename` argument
`python3.7 copernicus_extractor.py --mode e --country Ireland --tablename irish_data` 
will 

***NOTE : If a table name is not specified,a table name will be formatted from the name of the file provided. If a country is provided, the country's name will be appended to the end of the table name***

#### Worked Example:

###### Command: 

`python3.7 copernicus_extractor.py --mode e --country Ireland --tablename irish_data` 

1. The software will extract all data from the grib file that is contained within the bounding box surrounding Ireland.

2. A csv file will then be created containing the extracted data.

3. The contents of this file will be stored in a PostgreSQL database, within a table called 'irish_data' (as specified with the --tablename argument)

###### TODO: Documentation on analysis mode

