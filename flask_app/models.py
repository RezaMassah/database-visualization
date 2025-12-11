from flask_app import db

class UploadedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file = db.Column(db.LargeBinary, nullable=True) 

class DataFormat(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    format = db.Column(db.String(100), nullable=True) 

class UsersData(db.Model):
    username = db.Column(db.String(50), primary_key=True, unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(200), nullable=False)

