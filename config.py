scale_factor = 1000000000
sql_query = "INSERT INTO {} (timestamp, longitude, latitude, pollutant) VALUES (TO_TIMESTAMP({}, 'YYYY-MM-DD HH24:MI:SS'),{},{},{});"
db_name = 'copernicus_data'
user_name = '<username_here>'