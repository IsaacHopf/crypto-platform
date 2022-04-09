"""
Routes and views for the dashboard pages.
"""

from flask import Blueprint, render_template, session, request
from datetime import datetime

from crypto_platform import connect
from crypto_platform.dashboard import invest
from crypto_platform.dashboard.User import User

dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard', 
                      template_folder='templates',
                      static_folder='static')

@dashboard.route('/')
def home():
    """Handles the callback to Coinbase and renders the Dashboard page."""
    if 'tokens' in session: # If the tokens session variable already exists ...
        tokens = session['tokens'] # get the tokens from the session variable.
    else:
        try: # If the user has just logged in ...
            tokens = connect.coinbase_callback() # callback to Coinbase to get the tokens ...
            session['tokens'] = tokens # and store the tokens in a session variable.
            session['tokens_created_at'] = datetime.now()
        except: # If the user has not logged in or their tokens have expired ...
            return connect.coinbase_login() # redirect them to login.

    global user
    user = User(tokens)

    return render_template(
        'dashboard.html',
        title='Dashboard',
        #year=datetime.now().year,
        message='Your application description page.'
    )

@dashboard.route('/', methods=['POST'])
def home_post():
    selected_basket = request.form['baskets']
    investment_amount = request.form['investment-amount']
    print('SELECTED BASKET: ' + selected_basket)
    print('INVESTMENT AMOUNT: ' + investment_amount)

    return render_template(
        'dashboard.html',
        title='Dashboard',
        #year=datetime.now().year,
        message='Your application description page.',

    )

@dashboard.route('/testscripts')
def testscripts():
    invest.process_investments(user)

    return render_template(
        'dashboard.html',
        title='Dashboard',
        year=datetime.now().year
    )

@dashboard.route('/checkharvest')
def checkharvest():

    return render_template(
        'dashboard.html',
        title='Dashboard',
        #year=datetime.now().year,
        data = [['BTC', 0.00023333, 'LTC'], ['ETH', 0.0053333, 'DOT']]
    )

