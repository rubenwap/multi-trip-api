import itertools
import json
from datetime import datetime

import psycopg2
import requests
from flask import Flask, jsonify, render_template, request
from flask_wtf import FlaskForm
from psycopg2.extras import RealDictCursor
from redis import StrictRedis
from wtforms import DateField, IntegerField, StringField
from wtforms.validators import DataRequired


pg_config = {"host": "XXXXXXX", "database": "XXXXXXX", "user": "XXXXXXX", "password": "XXXXXXX"}
redis_config = {"host": "XXXXXXXXX", "password": "XXXXXXXXXXX", "port": 6379}

def postgres_insert(trips):
    """
	Does insertion in the SQL instance
	args:
		trips: JSON with list of trip options for a given route
	"""
    conn = psycopg2.connect(**pg_config)

    for trip in trips:
        sql_insert = """
			INSERT INTO journeys (source, destination, departure_datetime, arrival_datetime, carrier,
								vehicle_type, price, currency)
			VALUES (%(source)s,
					%(destination)s,
					%(departure_datetime)s,
					%(arrival_datetime)s,
					%(carrier)s,
					%(vehicle_type)s,
					%(price)s,
					%(currency)s);
			"""
        end_departure_date = trip["departure_datetime"]
        end_departure_date = end_departure_date[: end_departure_date.rindex("T")]

        end_arrival_date = trip["arrival_datetime"]
        end_arrival_date = end_arrival_date[: end_arrival_date.rindex("T")]

        values = {
            "source": trip["source"],
            "destination": trip["destination"],
            "departure_datetime": datetime.strptime(end_departure_date, "%Y-%m-%d"),
            "arrival_datetime": datetime.strptime(end_arrival_date, "%Y-%m-%d"),
            "carrier": trip["carrier"],
            "vehicle_type": trip["type"],
            "price": trip["price"],
            "currency": "EUR",
        }

        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql_insert, values)
            conn.commit()


def redis_insert(trips):
    """
	Does insertion in the Redis instance
	args:
		trips: JSON with trip options for a given route
	"""
    redis = StrictRedis(socket_connect_timeout = 3, **redis_config)
    
    source = trips[0]["source"]
    destination = trips[0]["destination"]
    end_date = trips[0]["departure_datetime"]
    end_date = end_date[: end_date.rindex("T")]
    departure = datetime.strptime(end_date, "%Y-%m-%d")

    key_name = f"prg_pw:journey:{source}_{destination}_{departure}_RegioJet"
    redis.setex(key_name, 60 * 60, json.dumps(trips))
