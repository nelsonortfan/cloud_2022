from flask_restful import Resource
from flask import request,Flask, request, send_from_directory
from datetime import datetime
from ..modelos import db, Task, User, UserSchema
import os
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, create_access_token

user_schema = UserSchema()

app = Flask(__name__)
app.config['UPLOADS_FOLDER'] = 'uploads/audios/'

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
      new_user = User(username=request.json["username"], password1=request.json["password1"], email=request.json["email"])
      access_token = create_access_token(identity=request.json['email'])
      db.session.add(new_user)
      db.session.commit()
      return {
         'message':'Usuario creado exitosamente',
         'access token':access_token
      }

