Title: How to create a virtualenv for web development for Eve and MongoDB
Date: 2014-02-08 21:16:14
Category: Python
Tags: python, virtualenv, web, mongodb, eve
Slug: web virtualenv
Author: Alexandre M. Savio
Summary: Create a virtualenv with web development framework Flask

## Installing Web development frameworks

 Create virtualenv for Sands (python 2.7.5)

    mkvirtualenv -p /usr/bin/python2.7 myweb

 Note that you are using the virtualenv: (myweb) in the beggining of the shell
line.

    pip install ipython[all]

#### First set of tools (en masse):

 Create requirements.txt:

    Cerberus
    Eve
    Events
    Flask
    Flask-Bootstrap
    Flask-Login
    Flask-Mail
    Flask-MongoRest
    Flask-Principal
    Flask-PyMongo
    Flask-Restless
    Flask-SSLify
    Flask-Script
    Flask-Security
    Flask-WTF
    Jinja2
    MarkupSafe
    Pygments
    Sphinx
    Werkzeug
    argparse
    docutils
    httpretty
    itsdangerous
    mongoengine
    fake-factory
    nose
    py-bcrypt
    pymongo
    python-dateutil
    requests
    six
    tornado
    urllib3
    wsgiref
    ujson


To install all modules in requirements.txt:

    pip install -r requirements.txt

#### Other options: simpler, maybe faster

<http://flask-pymongo.readthedocs.org/en/latest/>

<http://pythonhosted.org/Flask-Classy/>

<http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world>


#### Python-Eve seems to be a good solution after all:

<http://python-eve.org/index.html>

<http://blog.python-eve.org/eve-docs>
