## Run server

```shell
gunicorn --workers=1 --bind=127.0.0.1:8877 annoyingAI.app
```

## Query with e.g.

* with text input

```shell
curl -H "Content-Type: application/json" -X POST -d '{"text":"The U.S. will not go to war against North Korea.", "url":"http://www.foxnews.com/politics/2017/09/15/nikki-haley-to-north-korea-no-problem-letting-mattis-deal-with.html"}' -v localhost:8877/textcheck > out.txt
```

* with url input

```shell
curl -H "Content-Type: application/json" -X POST -d '{"text":"The U.S. will not go to war against North Korea.", "url":"http://www.foxnews.com/politics/2017/09/15/nikki-haley-to-north-korea-no-problem-letting-mattis-deal-with.html"}' -v localhost:8877/urlcheck > out.txt
```
