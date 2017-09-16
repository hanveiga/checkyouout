import falcon
from .checker import Resource, UrlResource, TextResource

api = application = falcon.API()

api.add_route('/factcheck', Resource())
api.add_route('/textcheck', TextResource())
api.add_route('/urlcheck', UrlResource())

# pip2.7 install gunicorn --user
# gunicorn --workers=1 --bind=127.0.0.1:8877 annoyingAI.app