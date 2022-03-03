"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from crypto_platform import app

from crypto_platform.coinbasescripts import connect
from crypto_platform.coinbasescripts import invest
from crypto_platform.coinbasescripts.User import User

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year
    )

@app.route('/coinbase_login')
def coinbase_login():
    return connect.coinbase_login()

@app.route('/redirect') # This is the page that users are redirected to after logging in to Coinbase
def redirect():
    """Renders the redirect page and handles coinbase_callback."""
    tokens = connect.coinbase_callback()

    global user
    user = User(tokens)

    #connect.getPrices()

    return render_template(
        'redirect.html',
        title='Redirect',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/testscripts') #this is a page that will only run scripts so we can test stuff
def testscripts():
    invest.process_investments(user)

    return render_template(
    'index.html',
    title='Home Page',
    year=datetime.now().year
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )
