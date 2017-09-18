# dFacto
Hack Zurich 2017 project

## About
The topic of reliability of news has been on the spotlight recently, mainly through the proliferation of fake news and alternative facts. In this project, we develop a prototype service with the intent to provide a judgement on the verificability of a statement by using the Reuters and SRF search and retrieval APIs as reliable sources. More info: https://devpost.com/software/h-jcxp24

## Setting up

First of all you should create a virtualenv with python3.5.

~~~
virtualenv --no-site-packages --distribute -p python /path/to/your/env
~~~

Than, using virtualenv, install package

~~~
. /path/to/your/env/bin/activate
~~~

Install requirements

~~~
pip install -r requirements.txt
~~~
