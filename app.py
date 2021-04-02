from flask import Flask
from flask import render_template, redirect, request

# Very useful when determining current date
import datetime

app = Flask(__name__)

notes = []

@app.route('/<name>', methods=['POST','GET'])
def test_page(name):
    name = name.capitalize()
    string = "Hello " + name
    return render_template("test.html", name=string)

@app.route('/', methods=['GET', 'POST'])
def index():
    headline = "Welcome Newcomer!"
    if request.method == "POST":
        if len(notes) > 0:
            del notes[0]
        note = request.form.get("note")
        notes.append(note)
        return redirect(f'\{notes[0]}')

    # Way to include the dates into the html in a selectable way
    dates = [101021,101121,101221,101321,101421,101521]
    # pass in headline variable to html
    return render_template("index.html", headline=headline,dates=dates)

# Huge Security Violation
# Remove debug when fully deployed
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)