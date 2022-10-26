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
    fecha_inicio = db.Column(db.String(50))
    fecha_final = db.Column(db.String(50))

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    email = db.Column(db.String(128))

# class EnumDictionary(fields.Field):
#     def _serialize(self, value, attr, obj, **kwards):
#         if value in None:
#             return None
#         return {'key':value.name, 'value':value.value}

class TaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        include_relationships = True
        load_instance = True
        

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
