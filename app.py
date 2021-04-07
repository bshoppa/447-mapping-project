from flask import Flask
from flask import render_template, redirect, request, send_file, send_from_directory

import datetime
import csv

app = Flask(__name__)


# initialize data
notes = []

facilities = {}

with open("CA-historical-data.csv") as csvfile:
    reader = csv.DictReader(csvfile, skipinitialspace=True)
    for row in reader:
        facilities[row['Facility.ID']] = {
            'Latitude': row['Latitude'],
            'Longitude': row['Longitude'],
            'Name': row['Name'],
            'Cases': row['Residents.Confirmed']
        }



# set up website urls
@app.route('/date', methods=['POST','GET'])
def get_prison_data():
    if request.method == 'POST':
        return facilities

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
    headline = "Welcome Newcomer!"
    if request.method == "POST":
        if len(notes) > 0:
            del notes[0]
        note = request.form.get("note")
        notes.append(note)
        print(note)
        return redirect(f'date={notes[0]}') # this line returns an error
    # Way to include the dates into the html in a selectable way
    dates = [101021,101121,101221,101321,101421,101521]
    # pass in headline variable to html


'''# Huge Security Violation
# Remove debug when fully deployed
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
'''
