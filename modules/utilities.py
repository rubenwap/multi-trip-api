import itertools
import json

import psycopg2
import requests
from flask import Flask, jsonify, render_template, request
from flask_wtf import FlaskForm
from psycopg2.extras import RealDictCursor
from redis import StrictRedis
from wtforms import DateField, IntegerField, StringField
from wtforms.validators import DataRequired

from .apis import get_city_id, trips_request, trips_cleanup

from .databases import postgres_insert, redis_insert

def main(origin, destination, departure, passengers, to_date):
    """
	Prepares the main variables and launches the functions defined above
	return:
		list of lists, where each sublist belongs to a group of origin/destination stations, considering
		that every city can have more than one station.
	"""

    display_trips = []
    departure_date = departure

    origins = get_city_id(origin)
    destinations = get_city_id(destination)

    for origin in origins:
        origin_name, origin_id = origin
        for destination in destinations:
            destination_name, destination_id = destination
            key_name = f"prg_pw:journey:{origin_name}_{destination_name}_{departure_date} 00:00:00_RegioJet"
            stored_value = redis.get(key_name)
            if stored_value is not None:
                display_trips.append(json.loads(stored_value.decode("utf-8")))
            else:
                trips = trips_request(origin_id, destination_id, departure_date)
                final_trips = trips_cleanup(origin_name, destination_name, trips, passengers, to_date)
                if final_trips is not None:
                    # placeholder for redis call
                    redis_insert(final_trips)
                    postgres_insert(final_trips)
                    display_trips.append([trip for trip in final_trips])

    return display_trips
