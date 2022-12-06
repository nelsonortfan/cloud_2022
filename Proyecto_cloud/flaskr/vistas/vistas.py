import shutil
from sqlite3 import IntegrityError
from os import remove
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, create_access_token,get_jwt
import os
import re
from sys import path
import shutil

from flask import request,Flask, request, send_from_directory
from flask_restful import Resource
from datetime import datetime
from werkzeug.utils import secure_filename
from os import remove
from ..modelos import db, Task, User, UserSchema, TaskSchema

# Import Google Client Libraries
from google.cloud import storage
from google.cloud import pubsub_v1

app = Flask(__name__)
app.config['UPLOADS_FOLDER'] = 'uploads/audios/'

user_schema = UserSchema()
task_schema = TaskSchema()



publisher = pubsub_v1.PublisherClient()
topic_path = 'projects/cloud-andes-conversion-tool/topics/Prueba-Audio'

class DownloadAudio(Resource):

   @jwt_required()
   def get(self,filename):
      try:
         claims = get_jwt()
         email = claims['sub']
         user= User.query.filter_by(email = email).first()
         id_usuario = user.id         
         task = Task.query.filter_by(id_usuario = id_usuario).first()

         


         if task is None:
            return {"mensaje": "Usuario no tiene el archivo {} en su repositorio".format(filename)},404
         else:
            mypath = task.path
            # print("La ruta obtenida de la BD es {}".format(mypath))
            filecomplete = mypath + filename
            # print("la ruta completa es ", filecomplete)
            # isExist = os.path.exists(filecomplete)
            # if isExist == True:
            #    return send_from_directory(mypath, filename)
            # else:
            #    return {"mensaje": "Archivo {} no existe en el repositorio del usuario".format(filename)},404 

            # Dowload file from GCP Bucket
            bucket_name = "audio_storage_cloud"
            source_blob_name = filecomplete
            destination_file_name = filename
            
            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(source_blob_name)
            blob.download_to_filename(destination_file_name)

            print(
               "Downloaded storage object {} from bucket {} to local file {}.".format(
                     source_blob_name, bucket_name, destination_file_name
               )
            )

            return send_from_directory('./', filename)

            # shutil.move(filename, '../uploads/audios/' + filename)
            # return send_from_directory('../uploads/audios/', filename)
            

      except Exception as e:
         return {"mensaje": "Archivo {} no existe".format(filename)},404 
   

class LoadAudio(Resource):

   @jwt_required()
   def post(self):

      claims = get_jwt()
      email = claims['sub']
      # print("el correo es ", email)
      user= User.query.filter_by(email = email).first()
      id = user.id
      # print("El id de usuario es ", id)
      myfile = request.files["file"]
      newformat = request.form["newFormat"]

      
      # Validate the new format
      if newformat == 'ogg' or newformat == 'mp3' or newformat == 'wma':
         
         # Validate the format of the uploaded file
         originalFileExtension = myfile.filename.split(".")[-1].lower()
         if originalFileExtension == 'mp3' or originalFileExtension =='wma' or originalFileExtension =='ogg':
            
            filename = secure_filename(myfile.filename)
            myPath = str(id) + "/"

            # validar si la ruta existe
            # mypath =os.path.join(app.config['UPLOADS_FOLDER'], str(id), "").replace('\\','/')
            # print("La ruta concatenada es ", mypath)
            # isExist = os.path.exists(mypath)
            # print("se valida si el folder existe y la respuesta es {}".format(isExist))

            # if isExist == False:
            #    print("creando el folder")
            #    os.mkdir(mypath)
            #    print("folder creado")

            # myfile.save(os.path.join(mypath, filename))   

            # Save the file in Bucket of GCP
            bucket_name = "audio_storage_cloud"
            destination_blob_name = myPath + filename
            contents = myfile

            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)

            blob.upload_from_file(request.files["file"], content_type='audio/mpeg')

            print(
               f"{destination_blob_name} with contents {contents} uploaded to {bucket_name}."
            )
            data = 'Mensaje 1'
            data = data.encode('utf-8')
            
            # Update task information in DB
            
            mydate = datetime.utcnow()
            mystatus = "uploaded"            
            task = Task(filename=filename,initialformat=originalFileExtension,path=myPath, newformat=newformat,timestamp=mydate,state=mystatus,id_usuario = id)
            attributes = {'id':str(id),'mydate': str(mydate),'mystatus': mystatus,'task': task.filename, 'initialformat':task.initialformat, 'newformat':task.newformat, 'filename':task.filename}
            future = publisher.publish(topic_path, data, **attributes)
            print(f'published message id {future.result()}')
            db.session.add(task)
            db.session.commit()
            return {"mensaje": "cargue archivo {} exitoso".format(filename)}
         else:
            return {"mensaje": "formato no valido de archivo de audio cargado"}
      else:
         return {"mensaje": "formato no valido a transformar"}

class DeleteAudio(Resource):
      @jwt_required()
      def delete(self):
         try:
            claims = get_jwt()
            email = claims['sub']
            # print("el correo es ", email)
            user= User.query.filter_by(email = email).first()
            id = user.id

            tasks = ([task_schema.dump(items) for items in Task.query.filter(Task.id_usuario == id)])

            for task in tasks:
               if(task['state'] == "uploaded"):
                  shutil.rmtree(os.path.join(app.config['UPLOADS_FOLDER'],str(id)))
                  return "Archivos"

         except Exception as e:
            return {"mensaje": "El archivo no existe"},404   


class ListAllTask(Resource):

   def get(self, id_usuario):
      args = request.args
      max = args.get('max')
      order = args.get('order')
      if(max):
         return [task_schema.dump(items) for items in Task.query.filter(Task.id_usuario == id_usuario).limit(max).all()]
      elif(order == "asc"):
         return [task_schema.dump(items) for items in Task.query.filter(Task.id_usuario == id_usuario).order_by(Task.id.asc()).all()]
      elif(order == "desc"):
         return [task_schema.dump(items) for items in Task.query.filter(Task.id_usuario == id_usuario).order_by(Task.id.desc()).all()]
      return [task_schema.dump(items) for items in Task.query.filter(Task.id_usuario == id_usuario)]



class VistaUpdateTask(Resource):
   
   def put(self, id_task):
      task_validation = Task.query.filter_by(id = id_task).all()

      if task_validation:
         task = Task.query.get(id_task)
         state = task.state

         if state == 'processed':
            name_file = task.filename[:-3]
            new_name_file = name_file + task.newformat
            path_file = str(task.id_usuario) + "/"
            # remove(path_file + new_name_file)

            # Remove object of GCP Bucket
            bucket_name = "audio_storage_cloud"
            blob_name = path_file + new_name_file

            storage_client = storage.Client()

            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.delete()

            # Update task information in DB
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
   
   


# def upload_blob_from_memory(bucket_name, contents, destination_blob_name):
#    """Uploads a file to the bucket."""

#    # The ID of your GCS bucket
#    # bucket_name = "your-bucket-name"

#    # The contents to upload to the file
#    # contents = "these are my contents"

#    # The ID of your GCS object
#    # destination_blob_name = "storage-object-name"

#    storage_client = storage.Client()
#    bucket = storage_client.bucket(bucket_name)
#    blob = bucket.blob(destination_blob_name)

#    blob.upload_from_string(contents)

#    print(
#       f"{destination_blob_name} with contents {contents} uploaded to {bucket_name}."
#    )
