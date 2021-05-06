from flask import Flask
from flask import render_template, redirect, request, send_file, send_from_directory
from flask_sqlalchemy import SQLAlchemy

import os
import json
from datetime import datetime
import csv
import string

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Place(db.Model):
    id_num = db.Column(db.Integer, primary_key = True)
    Facility_ID = db.Column(db.String(100), default = 0.0)
    Latitude = db.Column(db.String(100), nullable = False, default = 0.0)
    Longitude = db.Column(db.String(100), nullable = False, default = 0.0)
    name = db.Column(db.String(100), nullable = False)
    Cases = db.Column(db.String(100), nullable = False)
    Date = db.Column(db.String(100), nullable = False)
    County = db.Column(db.String(100), nullable = False, default = "Fluffy- if ur seeing this something wrong bro")


    def __repo__(self):
        return f"User('{self.id_num}', '{self.Latitude}', '{self.Longitude}')"

class County(db.Model):
    Cases = db.Column(db.String(100), nullable = False)
    Date = db.Column(db.String(100), nullable = False)
    Name = db.Column(db.String(100), nullable = False)
    id_num = db.Column(db.Integer, primary_key = True)

    def __repo__(self):
        return f"User('{self.id_num}', '{self.Latitude}', '{self.Longitude}')"


db.drop_all() # drops everything just in case
db.create_all() # creates everything new

tempCount = 0

# initialize data
notes = []

facilities = {}

counties = {}

mapID = []

for filename in os.listdir('countypolygons'):
    county_name = filename[:-9]
    #print(county_name)

    # initialize the county with our data structure (just an array with the geojson and the case number, which is 0 by default)
    counties[county_name] = json.load(open('countypolygons/' + filename))

counter = 0

print("loading facilities")
with open("CA-historical-data.csv") as csvfile:
    reader = csv.DictReader(csvfile, skipinitialspace=True)
    for row in reader:

        #print('facility', row['Date'])
        facilities[counter] = {
                'Latitude': row['Latitude'],
                'Longitude': row['Longitude'],
                'Name': row['Name'],
                'County': row['County'],
                'Cases' : row['Residents.Confirmed'],
                'Date': row['Date'],
                'Facility_ID' : row['Facility.ID']
            }
        counter = counter + 1
        '''
        if facilities.get(row['Facility.ID']) is None:
            # Initialize
            facilities[row['Facility.ID']] = {
                'Latitude': row['Latitude'],
                'Longitude': row['Longitude'],
                'Name': row['Name'],
                'County': row['County'],
                'Cases' : row['Residents.Confirmed'],
                'Date': row['Date']
            }
        else:
            facility = facilities[row['Facility.ID']]
            facility['Cases'] : row['Residents.Confirmed']
            facility['Date'] : row['Date']
            facility['Latitude'] : row['Latitude']
            facility['Longitude'] : row['Longitude']
            facility['Name'] : row['Name']
            facility['County'] : row['County']
            '''

print("loading counties")
with open("us-counties.csv") as csvfile:
    reader = csv.DictReader(csvfile, skipinitialspace=True)
    counter = 0
    for row in reader:
        # check if the county specified is in California. (mapping the rest of the us is unnecessary)
        if counties.get(row['county']):
            # if it is, add it to the database.

            counties[row['county']][1] = row['cases']
            #print('county', row['date'])
            newData = County(
                id_num = counter,
                Cases = row['cases'],
                Date = row['date'],
                Name = row['county']
            )
            db.session.add(newData)
            counter += 1

print("The number of entries in dict is : " , len(facilities))
print("The number of keys in dict is : " , len(facilities.keys()))
print("The number of values in dict is : " , len(facilities.values()))



for all in facilities:
    facility = facilities[all]
    #print(all, facility)
    newData = Place(id_num = all,
    Facility_ID = facility['Facility_ID'],
    Longitude = facility['Longitude'],
    Latitude = facility['Latitude'],
    name = facility['Name'],
    Cases = facility['Cases'],
    Date = facility['Date'],
    County = facility['County']
    )
    tempCount = tempCount + 1
    db.session.add(newData)

db.session.commit()

# locate the counties associated with facilities. add latest case data to the counties.
#for key in facilities:
    #facility = facilities[key]
    #if counties.get(facility['County']):
        #counties[facility['County']][1] += int(facility['Cases'])
    #else:
        #print(facility['County'], "not found")
    #    county_name = string.capwords(facility['County'].lower())
    #    try:
    #        if counties.get(county_name):
    #            #counties[county_name][1] += int(facility['Cases'])
    #        else:
    ##            print("\033[33mwarning: county not found", county_name, "; key",key,"not added to county display\033[0m")
    #    except (ValueError):
    #        print("\033[33mwarning: key", key, "does not have a case value\033[0m")

# print([key for key in counties])

'''
/data
parameters: date (optional)
output: a facilities dictionary, automatically converted to a json for the map to render
'''
doOnce = 0
@app.route('/data', methods=['POST'])
def get_prison_date():
    date = request.args.get("date")
    print("date input: %s" % date)
    global doOnce
    global mapID

    data = {}
    #data = Place.query.with_entities(Place.id_num).distinct()
    #data = db.query(Place.id_num.distinct())
    if date is None:
        subquery = Place.query.order_by(Place.Date.desc())
    else:
        subquery = Place.query.filter(Place.Date <= date).order_by(Place.Date.desc())
    query_value = Place.query.select_entity_from(subquery).group_by(Place.Facility_ID)
    for PlaceObject in query_value.all():
        #facility_id = facility_id[0]

        #PlaceObject = query_value.first() # get the first PlaceObject of the Facility ID before the date.
        myDict = {
            'Facility_ID' : PlaceObject.Facility_ID,
            'Latitude' : PlaceObject.Latitude,
            'Longitude' : PlaceObject.Longitude,
            'name' : PlaceObject.name,
            'Cases' : PlaceObject.Cases,
            'Date' : PlaceObject.Date,
            'County' : PlaceObject.County
        }
        data[PlaceObject.Facility_ID] = myDict
    
    if query_value.count() == 0:
        print("THERE ARE NO DATA ON THIS MAKE EVERYTHING ZERO")
        for changeValue in mapID:
            #changeValue['Cases'] = "0"
            mapID[changeValue]['Cases'] = 0
            print(mapID[changeValue]['Cases'])
    else:
        mapID = data
    
    #mapID = data.Facility_ID.distinct()
    
    doOnce = doOnce + 1
    

    '''
    for facility in facilities.items():
        if date is not None:
            #if facility[1].get("Date") <= date:
            #    data.append(facility)
        else:
            data.append(facility)
            '''
    return {'List' : mapID}

'''
/research.html
parameters: date (optional)
output: a page with the data in plaintext
'''
@app.route('/research.html', methods=['GET'])
def get_research_page():
    date = request.args.get("date")
    print("date input: %s" % date)
    #data = []
    #data = Place.query.filter_by(Date = date).all()
    #data = Place.query.order_by(Place.Date).all()
    data = Place.query.filter(Place.Date <= date).all()
    print("got from database  : " , data)
    '''
    for facility in facilities.items():
        if date is not None:
            if facility[1].get("Date") <= date:
                data.append(facility)
        else:
            data.append(facility)
            '''
    return render_template("research.html", dates = data)

'''
/counties
parameters: none
output: a json for website javascript, containing each geojson and evaluated county cases in the following format:
{
    '{county_name}': [{loaded countygeojson}, {cases}]
    ...
}
'''
@app.route('/counties', methods=['POST','GET'])
def send_counties():
    date = request.args.get("date")
    print("date input (/counties): %s" % date)
    if date is None:
        subquery = County.query.order_by(County.Date.desc())
    else:
        subquery = County.query.filter(County.Date <= date).order_by(County.Date.desc())
    query_value = County.query.select_entity_from(subquery).group_by(County.Name)
    data = {}
    for CountyObject in query_value.all():
        #facility_id = facility_id[0]

        #PlaceObject = query_value.first() # get the first PlaceObject of the Facility ID before the date.
        myDict = {
            'Cases' : CountyObject.Cases,
            'Date' : CountyObject.Date,
        }
        data[CountyObject.Name] = [counties[CountyObject.Name], myDict]
    import json
    # there's something horribly wrong with flask's dict - to - json system.
    # instead of a dict, we will return a string.
    return json.dumps(data)

'''
webhook:
serve public directories
'''
@app.route('/public/<path:path>')
def send_public(path):
    return send_from_directory('public', path)

'''
webhook:
user greeting page
'''
@app.route('/myname<name>', methods=['POST','GET'])
def test_page(name):
    print("forming response")
    name = name.capitalize()
    string = "Hello " + name
    return render_template("test.html", name=string)

'''
webhook:
serve index.html at the root directory, and redirect people who press the "Submit" button to research.html.
'''
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template("index.html")

    # input for date
    if request.method == "POST":
        date = request.form.get("date")
        print(date)
        return redirect('/research.html?date=%s' % date)


# Huge Security Violation
# Remove debug when fully deployed
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
