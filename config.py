scale_factor = 1000000000
#sql_query format $1:table name, $2:timestamp, $3: lat, $4: lon, $5:pollutant * scale factor
sql_query = "INSERT INTO {} (timestamp, co-ords, pollutant) VALUES (TO_TIMESTAMP({}, 'YYYY-MM-DD HH24:MI:SS'), ST_GeomFromText('POINT({} {})', 4326),{});"
db_name = 'copernicus_satellite_gis_data'
user_name = 'u180539'
table_name_format = "copernicus_data_{}"
table_exists_query_template = "SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='{}')"  
ireland_bounding_box = [-12.316, -4.98, 51.43, 55.36]