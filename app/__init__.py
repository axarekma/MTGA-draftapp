from flask import Flask
from flask_bootstrap import Bootstrap

import os

# Initialize the Flask application
app = Flask(__name__)
app.config.from_object("app.configuration.Config")
bootstrap = Bootstrap()
bootstrap.init_app(app)

from app import views
