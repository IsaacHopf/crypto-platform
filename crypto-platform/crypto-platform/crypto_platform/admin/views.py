"""
Routes and views for the admin pages.
"""

from flask import Blueprint, render_template

admin = Blueprint('admin', __name__, url_prefix='/admin', 
                  template_folder='templates',
                  static_folder='static')
