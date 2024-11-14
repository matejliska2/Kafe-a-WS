from flask import Flask, render_template, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from qr_code import generate_qr, register_user  

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' 
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qr_token = db.Column(db.String(256), unique=True, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/generate_qr')
def generate_qr_route():
    return generate_qr()  

@app.route('/register/<qr_token>')
def register(qr_token):
    if register_user(qr_token):  
        return redirect(url_for('login_success'))
    else:
        return "Invalid or expired QR code.", 401

@app.route('/login_success')
def login_success():
    return "Registration successful! You are now logged in."

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
