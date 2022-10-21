from xml.etree.ElementInclude import include
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    filename = db.Column(db.String(50))
    initialformat = db.Column(db.String(20)) 
    path = db.Column(db.String(50))
    newformat = db.Column(db.String(20))
    timestamp = db.Column(db.String(50))
    state = db.Column(db.String(20))
    id_usuario = db.Column(db.Integer)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50))
    password1 = db.Column(db.String(50))
    password2 = db.Column(db.String(50))
    email = db.Column(db.String(128))

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True