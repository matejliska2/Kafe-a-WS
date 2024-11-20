


import os
import openpyxl
import zipfile
from zipfile import BadZipFile
from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import json
''' 
mydb:
    table: kafe
        idkafe
        nazev
        mliko
        kafe

    table: priprava
        idpriprava
        kafe_idkafe
        uzivatel_iduzivatel
        datum
        počet
    table: uzivatel
        iduzivatel
        jmeno_primeni
        heslo
        narozeni
        admin
        
'''

app = Flask(__name__, template_folder='templates')

username = 'root'
password = ''
userpass = 'mysql+pymysql://' + username + ':' + password + '@'
server = '127.0.0.1'

dbname = 'Mydb'

app.config['SQLALCHEMY_DATABASE_URI'] = userpass + server + '/' + dbname
db = SQLAlchemy(app)

class Kafe(db.Model):
    idkafe = db.Column(db.Integer, primary_key=True)
    nazev = db.Column(db.String(45), nullable=False)
    mliko = db.Column(db.Integer, nullable=False)
    kafe = db.Column(db.Integer, nullable=False)

class Priprava(db.Model):
    idpriprava = db.Column(db.Integer, primary_key=True)
    kafe_idkafe = db.Column(db.Integer, db.ForeignKey('kafe.idkafe'), nullable=False)
    uzivatel_iduzivatel = db.Column(db.Integer, db.ForeignKey('uzivatel.iduzivatel'), nullable=False)
    datum = db.Column(db.DateTime, nullable=False)
    pocet = db.Column(db.Integer, nullable=False)

class Uzivatel(db.Model):
    iduzivatel = db.Column(db.Integer, primary_key=True)
    jmeno_primeni = db.Column(db.String(45), nullable=False)
    heslo = db.Column(db.String(45), nullable=False)
    narozeni = db.Column(db.Date, nullable=False)
    admin = db.Column(db.Boolean, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('insert_non_admin_user.html')

@app.route('/order_coffee')
def order_coffee():
    return render_template('insert_kafe_records.html')

@app.route('/overview')
def overview():
    orders = Priprava.query.all()
    return render_template('overview.html', orders=orders)

@app.route('/jobs')
def jobs():
    jobs = Kafe.query.all()
    return render_template('jobs.html', jobs=jobs)



@app.route('/submit_job', methods=['POST'])
def submit_job():
    description = request.form.get('job_description')
    file_path = os.path.join(app.root_path, 'data', 'jobs.json')
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump([], f)
    with open(file_path, 'r+') as f:
        if f.read() == '':
            data = []
        else:
            f.seek(0)
            data = json.load(f)
        data.append({'description': description})
        f.seek(0)
        json.dump(data, f)
        f.truncate()
    with open(file_path, 'r') as f:
        jobs = json.load(f)
    return render_template('jobs.html', jobs=jobs)

@app.route('/display_jobs')
def display_jobs():
    file_path = os.path.join(app.root_path, 'data', 'jobs.json')
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            jobs = json.load(f)
    else:
        jobs = []
    return render_template('jobs.html', jobs=jobs)

@app.route('/dump_task/<int:job_id>', methods=['POST'])
def dump_task(job_id):
    file_path = os.path.join(app.root_path, 'data', 'jobs.json')
    with open(file_path, 'r+') as f:
        data = json.load(f)
        del data[job_id]
        f.seek(0)
        json.dump(data, f)
        f.truncate()
    with open(file_path, 'r') as f:
        jobs = json.load(f)
    return render_template('jobs.html', jobs=jobs)
@app.context_processor
def inject_url_for():
    return dict(url_for=url_for)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)