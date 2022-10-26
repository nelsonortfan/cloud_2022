import subprocess
import sys
from flask import Flask
from modelos import db, Task
from datetime import datetime


def run():
    pass

app = Flask(__name__)


app.config['UPLOADS_FOLDER'] = 'uploads/audios/2/'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/osboxes/Proyecto_cloud/instance/tutorial_canciones.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myusuarioandes:123456@localhost:5432/books_store'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 


if __name__ == '__main__':

    db.init_app(app)
    subprocess.run(["python", "--version"])
    with app.app_context():
        tareas = db.session.query(Task).filter_by(state='uploaded')
        if tareas is None:
            run()
        else:
            for tarea in tareas:                
                mypath = tarea.path
                print("el tipo de variable de mypath es {} y su valor es {}".format(type(mypath),mypath))
                filename = tarea.filename
                newformat = tarea.newformat
                try:
                    print("Hola tarea con id {}, el path es {} para el archivo {} y con el nuevo formato {} \n".format(tarea.id,mypath,filename,newformat))
                    
                    print("vamos a mirar si permite procesar el cambio de audio")                 

                    lista = "ftransc -f " + str(newformat) + " " + str(filename) + " --force-root -w"
                    cmd = ['ftransc', '-f', str(newformat), str(filename), '--force-root','-w']
                    print(lista)
                    tarea.fecha_inicio = datetime.utcnow()
                    subprocess.call(cmd,cwd=mypath)                    
                    print("formato actualizado")
                    tarea.fecha_final = datetime.utcnow()
                    tarea.state="procesed"
                    db.session.add(tarea)
                    db.session.commit()
                except:
                    print("Error con la tarea que tiene id {}".format(tarea.id))
    run()


#subprocess.run(["ftransc", "-f", newformat, song,"--force-root","-w"],cwd='uploads/audios/2/')
