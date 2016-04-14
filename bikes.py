""" kYLE QUESTIONS
Shoud I really set up a new connection and cursor in each function or pass a cursor - connection pooling?
What is a good way to check validity of input.  Changed altitude to text type to avoid Integer error on load.
is it best to put imports in the individual functions or at the top - see 
"""

import requests
import psycopg2
import pandas as pd
from pandas.io.json import json_normalize
import datetime
import time
import collections

# a package for parsing a string into a Python datetime object
from dateutil.parser import parse 

def get_data():
	r = requests.get('http://www.citibikenyc.com/stations/json')
	return(r)

def build_citibike():
	# Connect to an existing database
	conn = psycopg2.connect("dbname=getting_started user=postgres password=Gatsby")

	with conn:
	    #open the cursor
	    cur = conn.cursor()

	    # set up the tables.
	    cur.execute("DROP TABLE IF EXISTS citibike_reference")

	    # CHANGED TO TEXT TYPE TO ELIMINATE INPUT ERRORS

	    cur.execute("CREATE TABLE citibike_reference (id integer PRIMARY KEY, \
	    	totalDocks integer NOT NULL DEFAULT 0, \
	    	city TEXT, \
		    altitude TEXT, \
		    stAddress2 TEXT, \
		    longitude NUMERIC NOT NULL DEFAULT 0, \
		    postalCode TEXT, \
		    testStation TEXT, \
		    stAddress1 TEXT, \
		    stationName TEXT, \
		    landMark TEXT, \
		    latitude NUMERIC NOT NULL DEFAULT 0, \
		    location TEXT);")
	return

def load_citibike(r):

	conn = psycopg2.connect("dbname=getting_started user=postgres password=Gatsby")

	
	#a prepared SQL statement we're going to execute over and over again
	sql = "INSERT INTO citibike_reference (id, totalDocks, city, altitude, stAddress2, \
		longitude, postalCode, testStation, stAddress1, stationName, landMark, latitude, location) \
		VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"


	#for loop to populate values in the database
	with conn:
		cur = conn.cursor()
		for station in r.json()['stationBeanList']:

			#####  ***** Need to do some bounds checking here ***** ######
			cur.execute(sql, (station['id'],station['totalDocks'],station['city'],station['altitude'], station['stAddress2'], station['longitude'],station['postalCode'],station['testStation'], station['stAddress1'],station['stationName'],station['landMark'],station['latitude'],station['location']))

	return

def build_available(r):
	conn = psycopg2.connect("dbname=getting_started user=postgres password=Gatsby")
	#extract the column from the DataFrame and put them into a list
	#from pandas.io.json import json_normalize

	df = json_normalize(r.json()['stationBeanList'])
	station_ids = df['id'].tolist() 

	#add the '_' to the station name and also add the data type for SQLite
	station_ids = ['_' + str(x) + ' INT' for x in station_ids]
	# station_ids = ['_' + str(x) for x in station_ids] # removing int here
	# print("************ printing station ids")
	# print(station_ids)

	#create the table
	#in this case, we're concatenating the string and joining all the station ids (now with '_' and 'INT' added)
	with conn:
		cur = conn.cursor()
		cur.execute("DROP TABLE IF EXISTS available_bikes")
		cur.execute("CREATE TABLE available_bikes (execution_time integer PRIMARY KEY, " + ", ".join(station_ids) + ")")

	return

def load_available_exec_time(r):
	conn = psycopg2.connect("dbname=getting_started user=postgres password=Gatsby")
	 #a package with datetime objects

	# 	 #take the string and parse it into a Python datetime object
	exec_time = parse(r.json()['executionTime'])
	# new_time = exec_time.strftime('%Y-%m-%dT%H:%M:%S')
	s =(exec_time - datetime.datetime(1970,1,1)).total_seconds()
	# print(new_time)

	with conn:
		cur = conn.cursor()
		cur.execute('INSERT INTO available_bikes (execution_time) VALUES(%s)', (s,))
	return

def iterate_available(): # take response object
	r = get_data()

	conn = psycopg2.connect("dbname=getting_started user=postgres password=Gatsby")
	# Then we iterate through the stations in the "stationBeanList":  **************** rest of this function untested ****************
	exec_time = parse(r.json()['executionTime'])
	s =(exec_time - datetime.datetime(1970,1,1)).total_seconds()
	
	id_bikes = collections.defaultdict(int) #defaultdict to store available bikes by station

	#loop through the stations in the station list
	for station in r.json()['stationBeanList']:
	    id_bikes[station['id']] = station['availableBikes']

	#iterate through the defaultdict to update the values in the database ******
	with conn:
		cur = conn.cursor()
		cur.execute('INSERT INTO available_bikes (execution_time) VALUES(%s)', (s,))
		for k, v in id_bikes.iteritems():

			cur.execute("UPDATE available_bikes SET _" + str(k) + " = " + str(v) + " WHERE execution_time = " + str(s) + ";")
			# cur.execute("UPDATE available_bikes SET _" + str(k) + " = " + str(v) + " WHERE execution_time = " + exec_time.strftime('%s') + ";")
	  #       UPDATE available_bikes SET _72 = 1 WHERE execution_time = exec_time.strftime('%s');

	return
	
def track_available():
	for x in range(61):
		print("Looping {}".format(x))
		iterate_available()
		print("finished iteration {}".format(x))
		time.sleep(60)
	return


def prep_db():
	r = get_data()
	build_citibike()
	load_citibike(r)
	build_available(r)
	# load_available_exec_time(r)
	track_available()
	# load_available(r)

	return
  
def main():
    prep_db()


if __name__ == "__main__":
    main()

