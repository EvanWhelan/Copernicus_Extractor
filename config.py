scale_factor = 1000000000
#sql_query format $1:table name, $2:timestamp, $3: lat, $4: lon, $5:pollutant * scale factor
sql_query = "INSERT INTO {} (timestamp, coordinates, pollutant) VALUES (TO_TIMESTAMP({}, 'YYYY-MM-DD HH24:MI:SS'), ST_GeomFromText('POINT({} {})', 4326),{});"
db_name = 'copernicus_satellite_gis_data'
username = 'evan'
table_name_format = "copernicus_data_{}"
table_exists_query_template = "SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='{}');"  
closest_point_query_template = "SELECT ST_X(coordinates), ST_Y(coordinates) FROM {} ORDER BY coordinates <-> st_setsrid(st_makepoint({}, {}), 4326) LIMIT 1;"
all_data_for_point_query_template = "SELECT timestamp, St_AsText(coordinates), pollutant FROM {} WHERE ST_X(coordinates) = {} AND ST_Y(coordinates) = {};"
all_tables_query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';"
all_data_query = "SELECT timestamp, St_AsText(coordinates), pollutant FROM {};"
drop_table_query_format = "DROP TABLE IF EXISTS {};"
csv_header = "timestamp, point, pollutant\n"