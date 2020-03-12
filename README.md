Flask Bootstrap
===============

**version 0.2.1**

Flask-Bootstrap is a simple **flask boilerplate** project for fast flask prototyping.
Just clone the project and you should be ready to go :)

Flask-Bootstrap is a modification of [Flask-Empty](https://github.com/italomaia/flask-empty)

Installation
------------

After cloned, install the requirements by calling

```shell
python3 -m venv env
./env/bin/pip install -r requirements.txt

cp .env.copy .env
# Edit .env to your needs
```

And you are ready to go :)


Differences with Flask-Empty
----------------------------

* We decided to automatically use SQLAlchemy features, so everything related to the database is enabled by default.
* We optimized the Test suite to implemente Tests for every Blueprints independantly.
* Finally, we added some features in the utils package to simplify the development of projects.
