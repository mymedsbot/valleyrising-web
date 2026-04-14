from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book')
def book():
    return render_template('book.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/conditions')
def conditions():
    return render_template('conditions.html')

@app.route('/new-patient')
def new_patient():
    return render_template('new-patient.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
