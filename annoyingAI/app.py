import falcon
from .checker import Resource, UrlResource, TextResource

api = application = falcon.API()

api.add_route('/factcheck', Resource())
api.add_route('/textcheck', TextResource())
api.add_route('/urlcheck', UrlResource())

# pip3 install gunicorn --user
# gunicorn --workers=1 --bind=127.0.0.1:8877 annoyingAI.app
# query with e.g.: curl -H "Content-Type: application/json" -X GET -d '{"text":"The U.S. will not go to war against North Korea.", "url":"http://www.foxnews.com/politics/2017/09/15/nikki-haley-to-north-korea-no-problem-letting-mattis-deal-with.html"}' -v localhost:8877/textcheck > out.txt