import os
import openpyxl
import zipfile
from zipfile import BadZipFile
from flask import Flask, render_template, url_for, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import json

app = Flask(__name__, template_folder='templates')

# Set the secret key for securing session data
app.secret_key = 'your_unique_secret_key_here'

# Database configuration
username = 'root'
password = ''
userpass = 'mysql+pymysql://' + username + ':' + password + '@'
server = '127.0.0.1'
dbname = 'Mydb'

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

@app.before_request
def check_login():
    # Redirect to login if not logged in
    if not session.get('logged_in') and request.endpoint != 'login':
        return redirect(url_for('login'))

    # Check admin status if logged in
    if 'logged_in' in session:
        user = Uzivatel.query.filter_by(iduzivatel=session['logged_in']).first()
        if user and not user.admin and request.endpoint == 'admin_dashboard':
            return redirect(url_for('login'))

def logged_in():
    return session.get('logged_in') is not None

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Uzivatel.query.filter_by(jmeno_primeni=username, heslo=password).first()
        if user:
            session['logged_in'] = user.iduzivatel
            session['is_admin'] = user.admin
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register')
def register():
    return render_template('insert_non_admin_user.html')

@app.route('/submit_non_admin_user', methods=['POST'])
def submit_non_admin_user():
    jmeno_primeni = request.form.get('username')
    heslo = request.form.get('password')
    narozeni = request.form.get('email')
    admin = False
    max_id = db.session.query(db.func.max(Uzivatel.iduzivatel)).scalar()
    u = Uzivatel(iduzivatel=(max_id or 0) + 1, jmeno_primeni=jmeno_primeni, heslo=heslo, narozeni=narozeni, admin=admin)
    db.session.add(u)
    db.session.commit()
    return "User added successfully"

@app.route('/order_coffee')
def order_coffee():
    kafe = Kafe.query.all()
    return render_template('insert_kafe_records.html', kafe=[k.nazev for k in kafe])


@app.route('/overview')
def overview():
    # Join Priprava, Kafe, and Uzivatel to get detailed order information
    orders = (
        db.session.query(
            Priprava.idpriprava.label('order_id'),
            Uzivatel.jmeno_primeni.label('customer_name'),
            Kafe.nazev.label('item_ordered'),
            Priprava.pocet.label('quantity'),
            Priprava.datum.label('date')
        )
        .join(Kafe, Priprava.kafe_idkafe == Kafe.idkafe)
        .join(Uzivatel, Priprava.uzivatel_iduzivatel == Uzivatel.iduzivatel)
        .all()
    )
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

@app.route('/display_coffees')
def display_coffees():
    kafe = Kafe.query.all()
    return render_template('insert_kafe_records.html', kafe=[k.nazev for k in kafe])

from datetime import datetime

@app.route('/insert_kafe_record', methods=['POST'])
def insert_kafe_record():
    # Get form data
    coffee_name = request.form.get('coffee_name')  # Coffee name from radio buttons
    coffee_quantity = request.form.get('coffee_quantity')  # Quantity from slider

    # Ensure user is logged in
    user_id = session.get('logged_in')
    if not user_id:
        return redirect(url_for('login'))

    # Find the coffee in the database
    selected_coffee = Kafe.query.filter_by(nazev=coffee_name).first()
    if not selected_coffee:
        return "Error: Coffee not found", 400

    # Get the current date and time
    current_date = datetime.now()

    # Create a new Priprava record
    new_priprava = Priprava(
        kafe_idkafe=selected_coffee.idkafe,
        uzivatel_iduzivatel=user_id,
        datum=current_date,
        pocet=coffee_quantity
    )

    # Add and commit to the database
    db.session.add(new_priprava)
    db.session.commit()

    return redirect(url_for('overview'))


@app.route('/display_pripravy')
def display_pripravy():
    pripravy = Priprava.query.join(Kafe, Priprava.kafe_idkafe == Kafe.idkafe).all()
    return render_template('priprava.html', pripravy=pripravy)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
