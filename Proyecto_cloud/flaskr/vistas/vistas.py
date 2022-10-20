from sqlalchemy.exc import IntegrityError
from flask_restful import Resource
from flask import request,Flask, request, send_from_directory
from flask_jwt_extended import jwt_required, create_access_token,get_jwt
from datetime import datetime
from ..modelos import db, Task, Usuario, TaskSchema
import os
from werkzeug.utils import secure_filename

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

class TaskDetail(Resource):

   #  @jwt_required()
    def get(self, id_task):
        return task_schema.dump(Task.query.get_or_404(id_task))

class CreateTask(Resource):

    def post(self, id_usuario):
      new_task = Task(filename=request.json["filename"],
                  initialformat= request.json["initialformat"],
                  path= request.json["path"],
                  newformat= request.json["newformat"],
                  timestamp= request.json["timestamp"],
                  state= request.json["state"],)
      usuario = Usuario.query.get_or_404(id_usuario)
      usuario.tasks.append(new_task)

      try:
            db.session.commit()
      except IntegrityError:
            db.session.rollback()
            return 'El usuario ya tiene un carrera con dicho nombre', 409

      return task_schema.dump(new_task)

class LoginUser(Resource):

   def post(self):
      usuario = Usuario.query.filter(Usuario.usuario == request.json["usuario"],
                                    Usuario.Password1 == request.json["Password1"]).first()
      db.session.commit()
      if usuario is None:
         return "El usuario no existe", 404
      else:
         token_de_acceso = create_access_token(identity=usuario.id)
         return {"mensaje": "Inicio de sesión exitoso", "token": token_de_acceso}

class CreateUser(Resource):
   def post(self):
        Password1 = request.json["Password1"]
        if (len(Password1)>8):
            usuario = Usuario.query.filter(Usuario.usuario == request.json["usuario"]).first()
            if usuario is None:
                nuevo_usuario = Usuario(usuario=request.json["usuario"], Password1=request.json["Password1"], Password2 = request.json["Password1"], correo= request.json["correo"])
                db.session.add(nuevo_usuario)
                db.session.commit()
                token_de_acceso = create_access_token(identity=nuevo_usuario.id)
                return {"mensaje": "usuario creado exitosamente", "token": token_de_acceso, "id": nuevo_usuario.id}
            else: return {"mensaje": "El usuario ya existe en la plataforma"} , 409

        else:
            return {"mensaje": "La contraseña debe de tener más de 8 caracteres"}, 409
