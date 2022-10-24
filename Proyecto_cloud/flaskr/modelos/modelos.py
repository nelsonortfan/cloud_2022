from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    filename = db.Column(db.String(50))
    initialformat = db.Column(db.String(20)) 
    path = db.Column(db.String(50))
    newformat = db.Column(db.String(20))
    timestamp = db.Column(db.String(50))
    state = db.Column(db.String(20))
    # id_usuario = db.Column(db.Integer)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id"))


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50))
    Password1 = db.Column(db.String(50))
    Password2 = db.Column(db.String(50))
    correo = db.Column(db.String(250))
    tasks = db.relationship('Task', cascade='all, delete, delete-orphan')

class TaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        include_relationships = False
        load_instance = True
