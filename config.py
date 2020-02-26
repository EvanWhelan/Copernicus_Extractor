scale_factor = 1000000000
#sql_query format $1:table name, $2:timestamp, $3: lat, $4: lon, $5:pollutant * scale factor
sql_insert_query_template = "INSERT INTO {} (timestamp, coordinates, pollutant, pollutant_name) VALUES (TO_TIMESTAMP({}, 'YYYY-MM-DD HH24:MI:SS'), ST_GeomFromText('POINT({} {})', 4326),{},{});"
db_name = 'copernicus_satellite_gis_data'
username = 'evan'
table_name_format = "copernicus_data_{}"
create_table_query_template = """
        CREATE TABLE IF NOT EXISTS {}(
            timestamp TIMESTAMP NOT NULL,
            coordinates GEOMETRY NOT NULL,
            pollutant DECIMAL NOT NULL,
            pollutant_name VARCHAR NOT NULL
        );
        """
table_exists_query_template = "SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='{}');"  
closest_point_query_template = "SELECT ST_X(coordinates), ST_Y(coordinates) FROM {} ORDER BY coordinates <-> st_setsrid(st_makepoint({}, {}), 4326) LIMIT 1;"
all_data_for_point_query_template = "SELECT timestamp, ST_X(coordinates), ST_Y(coordinates), pollutant, pollutant_name FROM {} WHERE ST_X(coordinates) = {} AND ST_Y(coordinates) = {} ORDER BY timestamp ASC;"
pollutant_for_point_query_template = "SELECT timestamp, ST_X(coordinates), ST_Y(coordinates), pollutant, pollutant_name FROM {} WHERE ST_X(coordinates) = {} AND ST_Y(coordinates) = {} and pollutant_name = '{}' ORDER BY timestamp ASC;"
all_tables_query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';"
all_data_query = "SELECT timestamp, ST_X(coordinates), ST_Y(coordinates), pollutant, pollutant_name FROM {} ORDER BY timestamp ASC;"
drop_table_query_format = "DROP TABLE IF EXISTS {};"
csv_header_row = ["timestamp", "lon", "lat", "pollutant", "pollutant_name"]
copernicus_species = {
    1 : "CO", 
    2 : "NH3",
    3 : "NMVOC",
    4 : "NO",
    5 : "NO2",
    6 : "O3",
    7 : "PANs",
    8 : "PM10", 
    9 : "PM2.5",
    10: "SO2"
}
    # core_pulltants being defined as the five pollutants that are used to calculate the AQIH (Air Quality Index for Health)
    # by the EPA
core_pollutants = ["O3", "PM10", "PM25", "NO2", "SO2"]
token = ""
copernics_url_format = "https://download.regional.atmosphere.copernicus.eu/services/CAMS50?token={}&grid=0.1&model=ENSEMBLE&package=ANALYSIS_{}_SURFACE&time=-24H-1H&referencetime={}&format=GRIB2"
copernicus_dir_name = "copernicus_api_dir_{}"
copernicus_api_file_format = "api_{}_{}_{}.grib2"
verification_dir_name_template = "location_verification_{}"
