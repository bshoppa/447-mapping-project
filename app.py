from flask import Flask
from flask import render_template, redirect, request, send_file, send_from_directory

import os
import json
from datetime import datetime
import csv
import string

app = Flask(__name__)


# initialize data
notes = []

facilities = {}

counties = {}

for filename in os.listdir('countypolygons'):
    county_name = filename[:-9]
    #print(county_name)
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
        #print(facility['County'], "not found")
        county_name = string.capwords(facility['County'].lower())
        try:
            if counties.get(county_name):
                counties[county_name][1] += int(facility['Cases'])
            else:
                print("warning: county not found", county_name, "; key",key,"not added to county display")
        except (ValueError):
            print("warning: key", key, "does not have a case value")

# print([key for key in counties])

'''
/data
parameters: date (optional)
output: a facilities dictionary, automatically converted to a json for the map to render
'''
@app.route('/data', methods=['POST'])
def get_prison_date():
    date = request.args.get("date")
    print("date input: %s" % date)
    if date is None:
        return facilities
    data = []
    for facility in facilities.items():
        if date is not None:
            if facility[1].get("Date") <= date:
                data.append(facility)
        else:
            data.append(facility)
    return data

'''
/research.html
parameters: date (optional)
output: a page with the data in plaintext
'''
@app.route('/research.html', methods=['GET'])
def get_research_page():
    date = request.args.get("date")
    print("date input: %s" % date)
    data = []
    for facility in facilities.items():
        if date is not None:
            if facility[1].get("Date") <= date:
                data.append(facility)
        else:
            data.append(facility)
    return render_template("research.html", dates=data)

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

    # input for date
    if request.method == "POST":
        curyear = datetime.now().year
        day = request.form.get("day")
        month = request.form.get('month')
        year = request.form.get('year')

        # error checking for date input
        if(int(day) > 31 or int(day) < 0):
            print("We day bad")
            return redirect('/')
        elif(int(year) > curyear):
            print("We year bad")
            return redirect('/')
        elif(int(month) > 12 or int(month) < 0):
            print("We month bad")
            return redirect('/')

        if(len(day) < 2):
            day = '0' + day
        elif(len(day) > 2):
            day = day[-2:]
        elif(len(month) > 2):
            month = month[-2:]
        elif(len(month) < 2):
            month = '0' + month

        date = year + "-" + month + "-" + day
        return redirect('/research.html?date=%s' % date)

# Huge Security Violation
# Remove debug when fully deployed
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
