from flaskr import create_app
from flask_restful import Api
from .modelos import db
from .vistas import LoadAudio,DownloadAudio, VistaSignIn, VistaLogIn
from flask_jwt_extended import JWTManager

app = create_app('default')
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

api = Api(app)
api.init_app(app)
api.add_resource(VistaSignIn, '/api/auth/signup')
api.add_resource(VistaLogIn, '/api/auth/login')
api.add_resource(LoadAudio, '/api/tasks')
api.add_resource(DownloadAudio, '/api/files/<string:filename>')

jwt = JWTManager(app)