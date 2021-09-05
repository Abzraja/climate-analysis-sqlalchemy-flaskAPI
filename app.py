import numpy as np
import datetime as dt
import os

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
file_dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
db_path = f"sqlite:///{file_dir}/hawaii.sqlite"
print(db_path)
engine = create_engine(db_path)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
print(Base.classes.keys())

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


# 3. Index Route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return "Routes available: <p><a href=/api/v1.0/precipitation>/api/v1.0/precipitation</a></p> <p><a href=/api/v1.0/stations>/api/v1.0/stations</a></p> <p><a href=/api/v1.0/tobs>/api/v1.0/tobs</a></p>"


# Routes
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'Precipitation' page...")
    
    session = Session(engine)
    
    most_recent_date = (
    session
    .query(Measurement.date)
    .order_by(Measurement.date.desc())
    .first()
    )

    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # Starting from the most recent data point in the database. 

    # Calculate the date one year from the last date in data set.
    # last date from string to date
    last_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d')

    # difference of 12 months
    delta = dt.timedelta(366)

    #last date - 12 month difference
    first_date = last_date - delta

    # Perform a query to retrieve the data and precipitation scores
    results = (
        session
        .query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date >= first_date)
        .all()
    )    

    session.close()

     # Create a dictionary from the row data and append to a list
    precipitation_results = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation_results.append(precipitation_dict)

    return jsonify(precipitation_results)

@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'Stations' page...")
    session = Session(engine)
    
    stations = (
    session
    .query(Station.station)
    .all()
    )

    session.close()

    all_stations = list(np.ravel(stations))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'tobs' page...")

    session = Session(engine)

    most_recent_date = (
    session
    .query(Measurement.date)
    .order_by(Measurement.date.desc())
    .first()
    )

    # Calculate the date one year from the last date in data set.
    # last date from string to date
    last_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d')

    # difference of 12 months
    delta = dt.timedelta(366)

    #last date - 12 month difference
    first_date = last_date - delta


    # Using the most active station id
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    last_year_temp = (
        session
        .query(Measurement.date, Measurement.tobs)
        .filter(Measurement.station == Station.station)
        .filter(Station.id == 7)
        .filter(Measurement.date >= first_date)
        .all()
        )    

    session.close()

     # Create a dictionary from the row data and append to a list
    tobs_results = []
    for date, tobs in last_year_temp:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_results.append(tobs_dict)

    return jsonify(tobs_results)


@app.route("/api/v1.0/<start>")
def start_tobs(start):
    print(f"Server received request for tobs from {start} date")

    session = Session(engine)

    tmax = (
    session
    .query(func.max(Measurement.tobs))
    .filter(Measurement.date >= start)
    .first()
    )

    tmin = (
    session
    .query(func.min(Measurement.tobs))
    .filter(Measurement.date >= start)
    .first()
    )

    tavg = (
    session
    .query(func.avg(Measurement.tobs))
    .filter(Measurement.date >= start)
    .first()
    )

    session.close()

    max_temp = list(np.ravel(tmin, tmax, tavg))
    #min_temp = list(np.ravel(tmin))
    #avg_temp = list(np.ravel(tavg))

    return jsonify(max_temp)

if __name__ == "__main__":
    app.run(debug=True)