from flaskr import create_app
from flask_restful import Api
from flask_jwt_extended import JWTManager
from .vistas import LoadAudio,DownloadAudio, ListAllTask,VistaSignIn,VistaLogIn, DeleteAudio, VistaUpdateTask


from .modelos import db

app = create_app('default')
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

api = Api(app)

api.add_resource(DownloadAudio, '/api/files/<string:filename>')
api.add_resource(LoadAudio, '/api/tasks')
api.add_resource(DeleteAudio, '/api/delete/')
api.add_resource(ListAllTask, '/api/<int:id_usuario>/show_tasks')
api.add_resource(VistaUpdateTask, '/api/tasks/<int:id_task>')
api.add_resource(VistaSignIn, '/api/auth/signup')
api.add_resource(VistaLogIn, '/api/auth/login')

jwt = JWTManager(app)
