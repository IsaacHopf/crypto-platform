"""
The flask application package.
"""

from flask import Flask

app = Flask(__name__, static_folder=None)

# Initialize the SQLite Datebase with SQLAlchemy
import os
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Register Blueprints
from crypto_platform.site.views import site
from crypto_platform.dashboard.views import dashboard
from crypto_platform.admin.views import admin

app.register_blueprint(site)
app.register_blueprint(dashboard)
app.register_blueprint(admin)
