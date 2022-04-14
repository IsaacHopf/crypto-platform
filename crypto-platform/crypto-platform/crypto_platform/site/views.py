"""
Routes and views for the flask application.
"""

from flask import Blueprint, render_template
from datetime import datetime

from crypto_platform import connect

site = Blueprint('site', __name__,
                 template_folder='templates',
                 static_folder='static')

@site.route('/test')
def test():
    return render_template(
        'test.html',
    )

@site.route('/')
@site.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year
    )

@site.route('/coinbase_login')
def coinbase_login():
    return connect.coinbase_login()

@site.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@site.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )
