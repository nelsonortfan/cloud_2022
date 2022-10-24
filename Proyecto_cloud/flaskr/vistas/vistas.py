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

   @jwt_required()
   def get(self, id_task):
        return task_schema.dump(Task.query.get_or_404(id_task))
