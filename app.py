from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns

app = Flask(__name__)

# Load CSV
csv_file = "DATA/FLIGHT_2.csv"
df = pd.read_csv(csv_file)

# # MongoDB Connection
# client = MongoClient("mongodb://localhost:27017/")
# db = client["flight_dashboard"]
# collection = db["flights"]


# Added flights list
added_flights = []

@app.route("/")
def dashboard():
    return render_template("index.html", page="dashboard")

@app.route("/search_delay", methods=["GET", "POST"])
def search_delay():
    delay_result = None
    if request.method == "POST":
        flight_number = request.form.get("flight_number", "").strip()
        origin = request.form.get("origin", "").strip()
        dest = request.form.get("dest", "").strip()
        distance = request.form.get("distance", "").strip()
        weather = request.form.get("weather", "").strip()
        dep_time = request.form.get("departure_time", "").strip()
        airline = request.form.get("airline", "").strip()

        # Search in CSV
        mask_csv = pd.Series([True]*len(df))
        if flight_number:
            mask_csv &= df['FlightNum'].astype(str).str.upper() == flight_number.upper()
        if origin:
            mask_csv &= df['Origin'].str.upper() == origin.upper()
        if dest:
            mask_csv &= df['Dest'].str.upper() == dest.upper()
        if distance:
            mask_csv &= df['Distance'] == int(distance)
        if weather:
            mask_csv &= df['Weather'].str.lower() == weather.lower()
        if airline:
            mask_csv &= df['Airline'].str.lower() == airline.lower()

        filtered_csv = df[mask_csv]

        # Search in added flights:-
        filtered_added = []
        for f in added_flights:
            if flight_number and f['FlightNo'].upper() != flight_number.upper():
                continue
            if origin and f['Origin'].upper() != origin.upper():
                continue
            if dest and f['Dest'].upper() != dest.upper():
                continue
            if distance and f['Distance'] != int(distance):
                continue
            if weather and f['Weather'].lower() != weather.lower():
                continue
            if airline and f['Airline'].lower() != airline.lower():
                continue
            filtered_added.append(f)

        # Result priority: CSV first, then added flights
        if not filtered_csv.empty:
            delay_result = f"{filtered_csv.iloc[0]['DelayMinutes']} minutes"
        elif filtered_added:
            delay_result = f"{filtered_added[0]['DelayMinutes']} minutes"
        else:
            delay_result = "Flight not found"

    return render_template("index.html", page="search", result=delay_result)

@app.route("/add_flight_page")
def add_flight_page():
    return render_template("index.html", page="add_flight")

@app.route("/add_flight", methods=["POST"])
def add_flight():
    try:
        flight = {
            "FlightNo": request.form['flight_no'],
            "Airline": request.form['airline'],
            "Origin": request.form['origin'],
            "Dest": request.form['dest'],
            "Distance": int(request.form['distance']),
            "Weather": request.form['weather'],
            "DepartureTime": request.form['departure_time'],
            "DelayMinutes": int(request.form['delay'])
        }
        added_flights.append(flight)
        return jsonify({"status": "success", "message": "Flight added successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/show_flights_page")
def show_flights_page():
    return render_template("index.html", page="show_flights")

@app.route("/show_flights")
def show_flights():
    # CSV data
    csv_flights = df.rename(columns={
        'FlightNum': 'FlightNo',
        'DepartureTime': 'DepartureTime',
        'DelayMinutes': 'DelayMinutes',
        'Airline': 'Airline',
        'Origin': 'Origin',
        'Dest': 'Dest',
        'Distance': 'Distance',
        'Weather': 'Weather'
    })[['FlightNo','Airline','Origin','Dest','Distance','Weather','DepartureTime','DelayMinutes']].to_dict(orient='records')

    all_flights = csv_flights + added_flights
    return jsonify(all_flights)

if __name__ == "__main__":
    app.run(debug=True)










