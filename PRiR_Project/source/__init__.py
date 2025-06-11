import os

from flask import Flask
from .db import init_db
from .routes import init_routes


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    app.config.from_pyfile('config.py', silent=True)
    
    init_db(app)
    
    init_routes(app)


    return app