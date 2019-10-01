from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

basedir = path.abspath(path.dirname(__file__))

# Main Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + path.join(basedir, "app.sqlite3")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Connect to Database (SQLite)
db = SQLAlchemy(app)

# Call for URL routes
from . import routes
