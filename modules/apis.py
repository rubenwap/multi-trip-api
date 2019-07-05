import itertools

import psycopg2
import requests
from flask import Flask, jsonify, render_template, request
from flask_wtf import FlaskForm
from psycopg2.extras import RealDictCursor
from redis import StrictRedis
from wtforms import DateField, IntegerField, StringField
from wtforms.validators import DataRequired



def get_city_id(city):
    """
	Gets a city and returns the ID
	args:
		city: The name of the city passed as argument
	returns:
		a tuple with the city name and its ID
	"""
    url = "https://www.studentagency.cz/data/wc/ybus-form/destinations-en.json"
    destinations = requests.get(url)

    for destination in destinations.json()["destinations"]:
        for each in destination["cities"]:
            if city.lower() == each["name"].replace("(bus)", "").strip().lower():
                return [(station["fullname"], station["id"]) for station in each["stations"]]


def trips_request(origin_id, destination_id, departure_date):
    """
	Returns the raw object from the ybus API for all the possible combinations
	args:
		origin_id: INT - The ID of the origin
		destination_id: INT - The ID of the destination
		departure_date: YYYY-MM-DD - The date of departure
	returns:
		List with dicts
	"""
    url = f"https://brn-ybus-pubapi.sa.cz/restapi/routes/search/simple?locale=en&departureDate={departure_date}&fromLocationId={origin_id}&toLocationId={destination_id}&fromLocationType=STATION&toLocationType=STATION&tariffs=REGULAR"
    trips = requests.get(url).json()
    return trips


def trips_cleanup(origin_name, destination_name, trips, passengers, to_date):
    """
	It returns a list of objects with the proper formatting we need
	args:
		origin_name: Name of source
		destination_name: Name of destination
		trips: Raw object with trips
	returns:
		final list of dicts that we can display/store
	"""
    final_trips = []
    for trip in trips["routes"]:
        final_trip = {}
        final_trip["departure_datetime"] = trip["departureTime"]
        final_trip["arrival_datetime"] = trip["arrivalTime"]
        final_trip["source"] = origin_name
        final_trip["destination"] = destination_name
        final_trip["price"] = trip["priceFrom"]
        final_trip["type"] = ", ".join(trip["vehicleTypes"])
        final_trip["source_id"] = trip["departureStationId"]
        final_trip["destination_id"] = trip["arrivalStationId"]
        final_trip["free_seats"] = trip["freeSeatsCount"]
        final_trip["carrier"] = "RegioJet"

        enough_seats = int(final_trip["free_seats"]) >= int(passengers)
        desired_date_range = to_date in final_trip["arrival_datetime"]

        if enough_seats & desired_date_range:
            final_trips.append(final_trip)
    # If we do simply return final_trips it will return an empty list if there are no combinations
    if final_trips:
        return final_trips


def combinations(origin, destination, departure):
    """
	Finds combinations for trips without direct option
	"""
    results_dict = {}
    sql_select = """
		SELECT 	a.source as origin, 
		a.departure_datetime as leaving_at,
		a.destination as first_stop, 
		a.arrival_datetime as arriving_at,
		a.carrier as operated_by,
		b.source as connection1, 
		b.departure_datetime as connection_leaving_at,
		b.destination as final_destination,
		b.carrier as connection_operated_by,
		b.arrival_datetime as final_arrival_time
		FROM journeys a
		INNER JOIN journeys b ON a.destination = b.source
		WHERE a.source like %(source)s AND b.destination like %(destination)s
		AND a.departure_datetime = %(departure)s
		"""

    values = {"source": f"{origin[:5]}%", "destination": f"{destination[:5]}%", "departure": f"{departure}%"}

    conn = psycopg2.connect(**pg_config)
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(sql_select, values)
        results_dict = cursor.fetchall()
    conn.close()
    return results_dict
