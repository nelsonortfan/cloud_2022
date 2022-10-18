from types import NoneType
from flask_restful import Resource
from flask import request, send_file
from datetime import datetime
from ..modelos import db,Upload
from io import BytesIO
import json
import base64
import pickle

import os
from flask import Flask, render_template, redirect, flash, request, send_from_directory
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['UPLOADS_FOLDER'] = 'uploads/images/'


class Prueba(Resource):    

     def post(self):
        
        myother = request.files["file"]
        print(request)
        newformat = request.form["newFormat"]
        print("El nuevo formato es {}".format(newformat))
        print("El typo de archivo es {}".format(myother))
        if newformat == 'ogg' or newformat == 'mp3' or newformat == 'wav':
         print(type(myother))
         nombre = myother.filename
         if nombre.endswith('.mp3') or nombre.endswith('.wav') or nombre.endswith('.ogg'):
            print("El titulo del archivo es {}".format(nombre))
            content = request.files['file'].read()
            #myother.save(nombre,buffer_size=16384)            
            filename = secure_filename(myother.filename)
            myother.save(os.path.join(app.config['UPLOADS_FOLDER'], filename))
            mydate = datetime.utcnow()
            mystatus = "uploaded"
            ## Guardar la info en BD
            upload = Upload(filename=nombre,data = content,status=mystatus,date=mydate)
            with open('ejemplo.pkl','wb') as f:
               pickle.dump(content,f,protocol=pickle.HIGHEST_PROTOCOL)
            db.session.add(upload)
            db.session.commit()
            ##
            return {"mensaje": "cargue archivo {} exitoso".format(nombre)}
         else:
            return {"mensaje": "formato no valido de archivo de audio cargado"}
        else:
         return {"mensaje": "formato no valido a transformar"}


class Descarga(Resource):

   def get(self,filename):
        descarga = Upload.query.filter_by(filename=filename).first()
        print(type(descarga))
        with open('ejemplo.pkl','rb') as f:
         archivo2 = pickle.load(f)
        print(type(archivo2)) 
        if type(descarga) != NoneType:
         print(type(descarga))
         #archivo =  send_file(BytesIO(descarga.data),download_name=filename,as_attachment=True)
         archivo =  send_file(BytesIO(archivo2),download_name=filename,as_attachment=True)
         print(type(archivo))         
         return archivo
        else:
         return {"mensaje": "Archivo no encontrado"},404