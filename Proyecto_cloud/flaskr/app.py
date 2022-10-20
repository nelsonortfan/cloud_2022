from flaskr import create_app
from flask_restful import Api
from .modelos import db
from .vistas import LoadAudio,DownloadAudio, ListAllTask

app = create_app('default')
app_context = app.app_context()
app_context.push()
api = Api(app)
api.init_app(app)

db.init_app(app)
db.create_all()

api.add_resource(LoadAudio, '/api/tasks')
api.add_resource(DownloadAudio, '/api/files/<string:filename>')
api.add_resource(ListAllTask, '/api/show_tasks')
