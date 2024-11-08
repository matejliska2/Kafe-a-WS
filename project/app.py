"""
test for a local -MySQL- database connection with XAMPP
requires PyMySQL, Flask-SQLAlchemy, Flask
.
make sure your virtualenv is activated!
make sure you have "started all" in XAMPP!
code below works for a MySQL database in XAMPP
- NOT XAMPP VM - on Mac OS
"""


from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy()
# create the app
app = Flask(__name__,template_folder='templates')

username = 'root'
password = ''
userpass = 'mysql+pymysql://' + username + ':' + password + '@'
server   = '127.0.0.1'

dbname   = '/Mydb'




# CHANGE NOTHING BELOW
# put them all together as a string that shows SQLAlchemy where the database is
app.config['SQLALCHEMY_DATABASE_URI'] = userpass + server + dbname 

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# initialize the app with Flask-SQLAlchemy
db.init_app(app)


# NOTHING BELOW THIS LINE NEEDS TO CHANGE
# this route will test the database connection - and nothing more
@app.route('/')
def testdb():
    
    try:
        db.session.query(text('1')).from_statement(text('SELECT 1')).all()
        return  render_template('index.html')
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text

if __name__ == '__main__':
    app.run(debug=True)
