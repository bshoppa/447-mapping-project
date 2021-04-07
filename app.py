from flask import Flask
from flask import render_template, redirect, request, send_file

import datetime
import csv

app = Flask(__name__)

notes = []

facilities = {}

with open("CA-historical-data.csv") as csvfile:
    reader = csv.DictReader(csvfile, skipinitialspace=True)
    for row in reader:
        # print(dict(row))
        facilities[row['Facility.ID']] = {
            'Latitude': row['Latitude'],
            'Longitude': row['Longitude'],
            'Name': row['Name'],
            'Cases': row['Residents.Confirmed']
        }

print("Data loaded.")

@app.route('/date', methods=['POST','GET'])
def get_prison_data():
    print("he")
    if request.method == 'POST':
        return facilities

def test_index_message():
    headline = "Welcome Newcomer!"
    if request.method == "POST":
        if len(notes) > 0:
            del notes[0]
        note = request.form.get("note")
        notes.append(note)
        return redirect(f'\{notes[0]}') # this line returns an error
    # Way to include the dates into the html in a selectable way
    dates = [101021,101121,101221,101321,101421,101521]
    # pass in headline variable to html


@app.route('/myname<name>', methods=['POST','GET'])
def test_page(name):
    print("forming response")
    name = name.capitalize()
    string = "Hello " + name
    return render_template("test.html", name=string)

@app.route('/public/icon1.png')
def get_icon():
    return send_file("public/icon1.png", mimetype = 'image/png')
@app.route('/public/icon2.png')
def get_icon2():
    return send_file("public/icon2.png", mimetype = 'image/png')


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")


'''# Huge Security Violation
# Remove debug when fully deployed
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
'''
