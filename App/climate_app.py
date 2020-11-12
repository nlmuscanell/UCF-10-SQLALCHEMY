import numpy as np
import datetime as dt
from datetime import timedelta, date
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#########################################################
# Database Setup
#########################################################
engine = create_engine("sqlite:///../Data/hawaii.sqlite")

# Reflect database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tableS
Measurement = Base.classes.measurement
Station = Base.classes.station


#########################################################
# Flask Setup
#########################################################

app = Flask(__name__)

@app.route("/")
def Home():
	"""List all available api routes."""
	return (
		f"Available Routes:<br/>"
		f"-------------------------------------------------------------------------------------------------------------<br/>"
		f"/api/v1.0/precipitation<br/>"
		f"/api/v1.0/stations<br/>"
		f"/api/v1.0/tobs<br/>"
		f"/api/v1.0/enter start date, Y-M-D<br/>"
		f"/api/v1.0/enter start date, Y-M-D/enter end date, Y-M-D<br/>"
		f"-------------------------------------------------------------------------------------------------------------<br/>"
	)

@app.route("/api/v1.0/precipitation")
def precipitation():
	# Create a session (link) from Python to the DB
	session = Session(engine)

	# Query for precipitation by date
	results = session.query(Measurement.date, Measurement.prcp).\
	order_by(Measurement.date).all()

	session.close()

	# Convert tuples into normal list
	precip = list(np.ravel(results))

	return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
	# Create a session (link) from Python to the DB
	session = Session(engine)

	# Query to get a list of station names
	sel = [Station.name]
	results = session.query(*sel).all()

	session.close()

	# Convert tuples into normal list
	stations = list(np.ravel(results))

	return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
	# Create our session (link) from Python to the DB
	session = Session(engine)

	# Find the date that is a year prior to the last date in the DB
	query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

	# Query the dates and temperature observations of the most active station for the last year of data
	results = session.query(Measurement.date, Measurement.tobs).\
	filter(Measurement.date >= query_date).\
	filter(Measurement.station == "USC00519281").\
	order_by(Measurement.date).all()

	session.close()

	# Convert tuples into normal list
	active_tobs = list(np.ravel(results))

	return jsonify(active_tobs)


@app.route("/api/v1.0/<start>")
def st_date(start):
	# Create a session (link) from Python to the DB
	session = Session(engine)

	# Define the dates as any date that is greater or equal to the start date
	start_date = dt.datetime.strptime(start, "%Y-%m-%d")

	# Query for min, mix, avg
	results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
	filter(Measurement.date >= start_date).all()

	session.close()

	# Convert tuples into normal list
	start_results = list(np.ravel(results))
	
	return jsonify(start_results)

@app.route("/api/v1.0/<start>/<end>")
def st_end(start, end):
	# Create a session (link) from Python to the DB
	session = Session(engine)

	# Define dates
	start_date = dt.datetime.strptime(start, "%Y-%m-%d")
	end_date = dt.datetime.strptime(end, "%Y-%m-%d")

	# Query for min, mix, avg between start and end date
	results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), \
	func.avg(Measurement.tobs)).filter(Measurement.date.between(start_date, end_date)).all()

	session.close()

	# Convert tuples into normal list
	start_end_results = list(np.ravel(results))

	return jsonify(start_end_results)

if __name__ == '__main__':
	app.run(debug=True)
