scale_factor = 1000000000
#sql_query format $1:table name, $2:timestamp, $3: lat, $4: lon, $5:pollutant * scale factor
sql_query = "INSERT INTO {} (timestamp, coordinates, pollutant) VALUES (TO_TIMESTAMP({}, 'YYYY-MM-DD HH24:MI:SS'), ST_GeomFromText('POINT({} {})', 4326),{});"
db_name = 'copernicus_satellite_gis_data'
username = 'u180539'
table_name_format = "copernicus_data_{}"
table_exists_query_template = "SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='{}')"  
closest_point_query_template = "SELECT ST_X(coordinates), ST_Y(coordinates) FROM {} ORDER BY coordinates <-> st_setsrid(st_makepoint({}, {}), 4326) LIMIT 1;"
all_data_for_point_query_template = "SELECT * FROM {} WHERE ST_X(coordinates) = {} AND ST_Y(coordinates) = {};"