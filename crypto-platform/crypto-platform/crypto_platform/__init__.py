"""
The flask application package.
"""

from flask import Flask

from .site.views import site
from .dashboard.views import dashboard
from .admin.views import admin

app = Flask(__name__, static_folder=None)

app.register_blueprint(site)
app.register_blueprint(dashboard)
app.register_blueprint(admin)


