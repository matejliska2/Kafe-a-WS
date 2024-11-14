import qrcode
import jwt
import datetime
from io import BytesIO
from main import db, User, app 
from flask import make_response

def generate_qr():
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    payload = {'exp': expiration_time, 'iat': datetime.datetime.utcnow()}
    qr_token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    
    new_user = User(qr_token=qr_token)
    db.session.add(new_user)
    db.session.commit()
    
    qr = qrcode.make(f"http://127.0.0.1:5000/register/{qr_token}")
    img_io = BytesIO()
    qr.save(img_io, 'PNG')
    img_io.seek(0)
    
    response = make_response(img_io.getvalue())
    response.headers.set('Content-Type', 'image/png')
    return response

def register_user(qr_token):
    try:
        jwt.decode(qr_token, app.config['SECRET_KEY'], algorithms=['HS256'])
        
        user = User.query.filter_by(qr_token=qr_token).first()
        if user:
            return True
        else:
            return False
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False
