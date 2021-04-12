from flask import Flask
from flask import render_template, redirect, request, send_file, send_from_directory

import os
import json
import datetime
import csv
import string

app = Flask(__name__)


# initialize data
notes = []

facilities = {}

counties = {}

for filename in os.listdir('countypolygons'):
    county_name = filename[:-9]
    print(county_name)
    counties[county_name] = [json.load(open('countypolygons/' + filename)), 0]

with open("CA-historical-data.csv") as csvfile:
    reader = csv.DictReader(csvfile, skipinitialspace=True)
    for row in reader:
        facilities[row['Facility.ID']] = {
            'Latitude': row['Latitude'],
            'Longitude': row['Longitude'],
            'Name': row['Name'],
            'Cases': row['Residents.Confirmed'],
            'Date': row['Date'],
            'County': row['County']
        }

for key in facilities:
    facility = facilities[key]
    if counties.get(facility['County']):
        counties[facility['County']][1] += int(facility['Cases'])
    else:
        print(facility['County'], "not found")
        county_name = string.capwords(facility['County'].lower())
        try:
            if counties.get(county_name):
                counties[county_name][1] += int(facility['Cases'])
        except (ValueError):
            print("nothing happened!!!!")

# set up website urls
@app.route('/date', methods=['POST','GET'])
def get_prison_data():
    print("he")
    if request.method == 'POST':
        return facilities



@app.route('/counties', methods=['POST','GET'])
def send_counties():
    return counties


@app.route('/public/<path:path>')
def send_public(path):
    return send_from_directory('public', path)

@app.route('/myname<name>', methods=['POST','GET'])
def test_page(name):
    print("forming response")
    name = name.capitalize()
    string = "Hello " + name
    return render_template("test.html", name=string)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template("index.html")

    if request.method == "POST":
        #if len(notes) > 0:
        #    del notes[0]
        day = request.form.get("day")
        month = request.form.get('month')
        year = request.form.get('year')
        #if(int(day) > 31 or int(day) < 0):

        date = year + "-" + month + "-" + day
        #notes.append(notes)
        #print(notes)
        return redirect(f'/date/{date}')

    # Way to include the dates into the html in a selectable way
    # dates = [101021,101121,101221,101321,101421,101521]
    # pass in headline variable to html


# Huge Security Violation
# Remove debug when fully deployed
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
