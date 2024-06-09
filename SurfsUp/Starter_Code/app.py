# Import the dependencies.
import numpy as np
import re
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Starter_Code/Resources/hawaii.sqlite", pool_pre_ping= True)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD)"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Jsonify precipitation data for one year."""
    #Query Measurement
    results = (session.query(measurement.date, measurement.tobs)
                    .order_by(measurement.date))
    
    #Create a dictionary
    precipitation_date_tobs = []
    for each_row in results:
        dt_dict = {}
        dt_dict["date"] = each_row.date
        dt_dict["tobs"] = each_row.tobs
        precipitation_date_tobs.append(dt_dict)

    return jsonify(precipitation_date_tobs)


@app.route("/api/v1.0/stations") #Return a JSON list of stations from dataset
def stations():
    """Jsonify a list of the stations"""
    #Query Stations
    results = session.query(station.name).all()

    #Convert list of tuples into normal list
    station_details = list(np.ravel(results))

    return jsonify(station_details)


@app.route("/api/v1.0/tobs") #Query the dates and temperature observations of the most active station for the last year of data
def tobs():
    """Return the temperatures from the most active station."""
    #Query the last 12 months of temperature observation data for the most active station
    start_date = '2016-08-23'
    sel = [measurement.date, measurement.tobs]
    station_temps = session.query(*sel).\
            filter(measurement.date >= start_date, measurement.station == 'USC00519281').\
            group_by(measurement.date).\
            order_by(measurement.date).all()
    
    #Return a dictionary with the date
    observation_dates = []
    temperature_observations = []

    for date, observation in station_temps:
        observation_dates.append(date)
        temperature_observations.append(observation)

    most_active_dict = dict(zip(observation_dates, temperature_observations))

    return jsonify(most_active_dict)


@app.route('/api/v1.0/<start>')
def start(start):
    """Jsonify Temperature data from a start date"""
    
    #Temp Dictionaries and results to jsonify
    temp_results = []
    temp_dict = {}

    #Find the max temperature
    max_temp = session.query(func.max(measurement.tobs)).\
        filter(measurement.date >= start).scalar()
    temp_dict['max temp'] = max_temp

    #Find the min temperature
    min_temp = session.query(func.min(measurement.tobs)).\
        filter(measurement.date >= start).scalar()
    temp_dict['min temp'] = min_temp

    #Find the average temperature
    avg_temp = session.query(func.avg(measurement.tobs)).\
        filter(measurement.date >= start).scalar()
    temp_dict['avg temp'] = avg_temp
    temp_results.append(temp_dict)

    return jsonify(temp_results)


@app.route('/api/v1.0/<start>/<end>')
def start_and_end(start, end):
    """Jsonify temperature data from a start and end date."""
    # Temp Dictionaries and results to jsonify
    se_temp_results = []
    se_temp_dict = {}

    # Find the max temperature
    max_temp = session.query(func.max(measurement.tobs)).\
        filter(measurement.date >= start, measurement.date <= end).scalar()
    se_temp_dict['max temp'] = max_temp

    # Find the min temperature
    min_temp = session.query(func.min(measurement.tobs)).\
        filter(measurement.date >= start, measurement.date <= end).scalar()
    se_temp_dict['min temp'] = min_temp

    # Find the average temperature
    avg_temp = session.query(func.avg(measurement.tobs)).\
        filter(measurement.date >= start, measurement.date <= end).scalar()
    se_temp_dict['avg temp'] = avg_temp
    se_temp_results.append(se_temp_dict)

    return jsonify(se_temp_results)

session.close()

if __name__ == "__main__":
    app.run(debug=True)