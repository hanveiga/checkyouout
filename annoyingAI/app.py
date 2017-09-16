import falcon
from checker import Resource

api = application = falcon.API()

checker_model = Resource()
api.add_route('/check', checker_model)

# pip2.7 install gunicorn --user
# gunicorn --workers=1 --bind=127.0.0.1:8877 annoyingAI.app