import subprocess
import sys
from flask import Flask
from modelos import db, Task


def run():
    pass

app = Flask(__name__)


app.config['UPLOADS_FOLDER'] = 'uploads/audios/2/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tutorial_canciones.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 


if __name__ == '__main__':
    #newformat = sys.argv[1]
    #song = sys.argv[2]
    #format = "." + newformat
    #print("El valor del formato ingresado es {} y el valor concatenado es {} para la cancion {}".format(song,format,song))

    db.init_app(app)
    subprocess.run(["python", "--version"])
    with app.app_context():
        tareas = db.session.query(Task).filter_by(state='uploaded')
        if tareas is None:
            run()
        else:
            for tarea in tareas:
                #print("El id de la tarea es {} y el path es {}\n".format(tarea.id, tarea.path))
                mypath = tarea.path
                print("el tipo de variable de mypath es {} y su valor es {}".format(type(mypath),mypath))
                filename = tarea.filename
                newformat = tarea.newformat
                try:
                    print("Hola tarea con id {}, el path es {} para el archivo {} y con el nuevo formato {} \n".format(tarea.id,mypath,filename,newformat))
                    #subprocess.run(["ftransc", "-f", newformat, song,"--force-root","-w"],cwd='uploads/audios/2/')
                    #subprocess.run(["ftransc", "-f", newformat, song,"--force-root","-w"],cwd=mypath)
                    if tarea.id == 202 or tarea.id == 150:
                        tarea.state="procesed"
                        db.session.add(tarea)
                        db.session.commit()
                except:
                    print("Error con la tarea que tiene id {}".format(tarea.id))
    run()



#subprocess.run(["ftransc", "-f", newformat, song,"--force-root","-w"],cwd='uploads/audios/2/')
