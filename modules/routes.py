import os
from flask import Flask, jsonify, render_template, request
from flask_wtf import FlaskForm

from wtforms import DateField, IntegerField, StringField
from wtforms.validators import DataRequired

from .utilities import main

SECRET_KEY = os.urandom(32)

app = Flask(__name__, static_folder="static")
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["SECRET_KEY"] = SECRET_KEY

@app.errorhandler(500)
def error_500(exception):
    """ Error 500 return """
    return str(exception), 500, {'Content-Type': 'text/plain'}


@app.route("/trips", methods=["GET", "POST"])
def view_trips():
    class FindTrips(FlaskForm):
        origin = StringField("origin", validators=[DataRequired()])
        destination = StringField("destination", validators=[DataRequired()])
        departing = DateField("departing", validators=[DataRequired()], format="%Y-%m-%d")
        arriving = DateField("arriving", validators=[DataRequired()], format="%Y-%m-%d")
        passengers = IntegerField("passengers", validators=[DataRequired()])

    form = FindTrips()
    return render_template("search.html", form=form)


@app.route("/results", methods=["POST", "GET"])
def results():
    if request.method == "POST":
        result = request.form
        origin = result.get("origin")
        destination = result.get("destination")
        departure = result.get("departing")
        to_date = result.get("arriving")
        passengers = int(result.get("passengers"))
        data = main(origin, destination, departure, passengers, to_date)
        return render_template("results.html", trips=data)


@app.route("/search", methods=["GET"])
def get_trips():
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    departure = request.args.get("departure")
    passengers = request.args.get("passengers")
    to_date = request.args.get("to_date")
    return jsonify(main(origin, destination, departure, passengers, to_date))


@app.route("/combinations", methods=["GET"])
def get_combinations():
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    departure = request.args.get("departure")

    return jsonify(combinations(origin, destination, departure))
