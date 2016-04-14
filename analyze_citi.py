# analyze citibike data

import pandas as pd
import psycopg2

conn = psycopg2.connect("dbname=getting_started user=postgres password=Gatsby")

with conn:
#open the cursor
	cur = conn.cursor()
	pd = pd.read_sql_query("SELECT * FROM available_bikes ORDER BY execution_time", conn, index_col='execution_time')