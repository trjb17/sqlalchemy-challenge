# Import the dependencies
from flask import Flask, jsonify
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import numpy as np  # Import numpy for np.ravel()
import pandas as pd
import datetime as dt
#################################################
# Database Setup
#################################################

# Create an engine to connect to the SQLite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the tables from the database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

# Create an app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Define the home page
@app.route("/")
def home():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"<a href='/api/v1.0/start_date'>/api/v1.0/start_date</a><br/>"
        f"<a href='/api/v1.0/start_date/end_date'>/api/v1.0/start_date/end_date</a>"
    )

# Define the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date 1 year ago from the last data point in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Query to retrieve the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()
    
    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_data)

# Define the stations route
@app.route("/api/v1.0/stations")
def stations():
    # Query to retrieve the list of stations
    results = session.query(Station.station).all()
    
    # Convert the query results to a list
    stations_list = list(np.ravel(results))
    
    return jsonify(stations_list)

# Define the temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date 1 year ago from the last data point in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Query to retrieve the temperature observations of the most active station for the previous year of data
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= prev_year).all()
    
    # Convert the query results to a list of dictionaries
    tobs_data = [{"date": date, "tobs": tobs} for date, tobs in results]
    
    return jsonify(tobs_data)

# Define the start date route
@app.route("/api/v1.0/<start>")
def start_date(start):
    # Query to calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    # Convert the query results to a list of dictionaries
    start_date_data = [{"TMIN": result[0], "TAVG": result[1], "TMAX": result[2]} for result in results]
    
    return jsonify(start_date_data)

# Define the start and end date route
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Query to calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    # Convert the query results to a list of dictionaries
    start_end_date_data = [{"TMIN": result[0], "TAVG": result[1], "TMAX": result[2]} for result in results]
    
    return jsonify(start_end_date_data)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)