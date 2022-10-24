from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, create_access_token,get_jwt
import os
import re
from flask import request,Flask, request, send_from_directory
from flask_restful import Resource
from datetime import datetime
from werkzeug.utils import secure_filename
from os import remove
from ..modelos import db, Task, User, UserSchema, TaskSchema


user_schema = UserSchema()
task_schema = TaskSchema()

app = Flask(__name__)
app.config['UPLOADS_FOLDER'] = 'uploads/audios/'

task_schema = TaskSchema()

class DownloadAudio(Resource):

   def get(self,filename):
      try:
         return send_from_directory(app.config['UPLOADS_FOLDER'], filename)
      except Exception as e:
         return {"mensaje": "Archivo {} no existe".format(filename)},404 
   

class LoadAudio(Resource):

   def post(self):
      myfile = request.files["file"]
      newformat = request.form["newFormat"]
      if newformat == 'ogg' or newformat == 'mp3' or newformat == 'wav':
         originalFileExtension = myfile.filename.split(".")[-1].lower()
         if originalFileExtension == 'mp3' or originalFileExtension =='wav' or originalFileExtension =='ogg':
            filename = secure_filename(myfile.filename)
            myfile.save(os.path.join(app.config["UPLOADS_FOLDER"], filename))
            mydate = datetime.utcnow()
            mystatus = "uploaded"
            task = Task(filename=filename,initialformat=originalFileExtension,path=app.config["UPLOADS_FOLDER"], newformat=newformat,timestamp=mydate,state=mystatus)
            db.session.add(task)
            db.session.commit()
            return {"mensaje": "cargue archivo {} exitoso".format(filename)}
         else:
            return {"mensaje": "formato no valido de archivo de audio cargado"}
      else:
         return {"mensaje": "formato no valido a transformar"}

class VistaSignIn(Resource):

   def post(self):
      username = request.json["username"]
      pass1 = request.json["password1"]
      pass2 = request.json["password2"]
      email = request.json["email"]

      regular_phrase = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
      
      email_validation = re.match(regular_phrase, email) is not None
      email_existing = User.query.filter_by(email = email).all()

      if len(pass1) >= 8 and pass1 == pass2 and email_validation and len(email_existing) == 0:
         new_user = User(username=username, password=pass1, email=email)
         access_token = create_access_token(identity=email)
         db.session.add(new_user)
         db.session.commit()
         return {
            'message':'Usuario creado exitosamente',
            'access token':access_token
         }, 200
      elif len(pass1) < 8:
         return {'mensaje':'Contraseña debe contener al menos 8 caracteres'}, 401
      elif pass1 != pass2:
         return {'mensaje':'Contraseña 2 no coincide'}, 401
      elif len(email_existing) != 0:
         return {'mensaje':'Email existente'}, 401
      else:
         return {'mensaje':'Correo invalido'}, 401

      
class VistaLogIn(Resource):
   def post(self):
      email = request.json["email"]
      password = request.json["password"]

      user = User.query.filter_by(email = email, password = password).all()
      
      if user:
         access_token = create_access_token(identity=email)
         return {
            'message':'LogIn exitoso',
            'access token':access_token
         }, 200
      else:
         return {'mensaje':'Email de usuario o contraseña incorrectos'}, 401

class VistaUpdateTask(Resource):
   @jwt_required()
   def put(self, id_task):
      task_validation = Task.query.filter_by(id = id_task).all()

      if task_validation:
         task = Task.query.get(id_task)
         state = task.state

         if state == 'processed':
            path_file = task.path
            name_file = task.filename[:-3]
            new_name_file = name_file + task.newformat
            remove( path_file + new_name_file )

            task.newformat = request.json["newFormat"]
            task.state = "uploaded"
            db.session.commit()

            return {
               'mensaje':'Tarea actualizada correctamente',
               'Tarea': task_schema.dump(task)
            }, 200
         else:
            task.newformat = request.json["newFormat"]
            db.session.commit()
            return {
               'mensaje':'Tarea actualizada correctamente',
               'Tarea': task_schema.dump(task)
            }, 200
      else:
         return {'mensaje':'Tarea no existente'}, 404

   @jwt_required()
   def get(self, id_task):
        return task_schema.dump(Task.query.get_or_404(id_task))