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

# Initialize Flask-Mail and Configure the Sender Email
from flask_mail import Mail

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_DEFAULT_SENDER'] = 'baskinthecrypto@gmail.com'
app.config['MAIL_USERNAME'] = 'baskinthecrypto@gmail.com'
app.config['MAIL_PASSWORD'] = 'ckzsxzyqprfekyok'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# Register Blueprints
from crypto_platform.site.views import site
from crypto_platform.dashboard.views import dashboard
from crypto_platform.admin.views import admin

app.register_blueprint(site)
app.register_blueprint(dashboard)
app.register_blueprint(admin)
