"""
Routes and views for the dashboard pages.
"""

from flask import Blueprint, render_template, session, request
from datetime import datetime, timedelta
import re
from werkzeug import Response

from crypto_platform import connect
from crypto_platform.dashboard import invest, taxlossharvest
from crypto_platform.dashboard.User import User

dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard', 
                      template_folder='templates',
                      static_folder='static')

@dashboard.route('/')
def home():
    """Handles the callback to Coinbase and renders the Dashboard page."""
    user = create_user()

    if isinstance(user, Response): # If the user needs to login ...
        return user # redirect them to login.
    else:
        return render_template(
            'dashboard.html',
            native_currency = user.native_currency,
            baskets=get_basket_names(),
            step_one_visibility = '',
            step_two_visibility = 'hidden'
        )

@dashboard.route('/selectbasket', methods=['POST'])
def selectbasket():
    """Handles selecting a basket and investing."""
    user = create_user()

    if isinstance(user, Response): # If the user needs to login ...
        return user # redirect them to login.
    else:

        try:
            selected_basket_name = request.form['baskets']
            investment_amount = float(request.form['investment-amount'])
        except:
            return render_template(
            'dashboard.html',
            native_currency = user.native_currency,
            baskets=get_basket_names(),
            step_one_visibility = '',
            step_two_visibility = 'hidden'
        )
        else:
            #selected_basket = BasketModel.query.filter_by(name='selected_basket')
            #get crypto percentages
            selected_basket = [['BTC', 0.4], ['ETH', 0.3], ['LTC', 0.2], ['ADA', 0.1]]

            if re.match("^\d*", str(investment_amount)): # If the basket name and investment amount exist and if the investment amount is a number ...
                invest.make_investment(user, selected_basket, investment_amount) # make the investment.

            return render_template(
                'dashboard.html',
                native_currency = user.native_currency,
                baskets=get_basket_names(),
                step_one_visibility = '',
                step_two_visibility = 'hidden'
            )

@dashboard.route('/withdraw')
def withdraw():
    """Handles withdrawing."""
    user = create_user()

    if isinstance(user, Response): # If the user needs to login ...
        return user # redirect them to login.
    else:

        basket = [['BTC', 0.4], ['ETH', 0.3], ['LTC', 0.2], ['ADA', 0.1]]
        invest.make_withdrawal(user, basket, user.get_cash_wallet_balance())

        return render_template(
            'dashboard.html',
            native_currency = user.native_currency,
            baskets=get_basket_names(),
            step_one_visibility = '',
            step_two_visibility = 'hidden'
        )


@dashboard.route('/testscripts')
def testscripts():
    user = create_user()

    if isinstance(user, Response): # If the user needs to login ...
        return user # redirect them to login.
    else:

        taxlossharvest.process_investments(user)

        return render_template(
            'dashboard.html',
            native_currency = user.native_currency,
            baskets=get_basket_names(),
            step_one_visibility = '',
            step_two_visibility = 'hidden'
        )

@dashboard.route('/checkharvest')
def checkharvest():
    user = create_user()

    if isinstance(user, Response): # If the user needs to login ...
        return user # redirect them to login.
    else:

        data = taxlossharvest.process_investments(user)

        return render_template(
            'dashboard.html',
            native_currency = user.native_currency,
            baskets=get_basket_names(),
            data=data,
            step_one_visibility = 'hidden',
            step_two_visibility = ''
        )

@dashboard.route('/testharvest')
def testharvest():
    user = create_user()

    if isinstance(user, Response): # If the user needs to login ...
        return user # redirect them to login.
    else:

        data = taxlossharvest.use_test_data(user)

        return render_template(
            'dashboard.html',
            native_currency = user.native_currency,
            baskets=get_basket_names(),
            data=data,
            step_one_visibility = 'hidden',
            step_two_visibility = ''
        )

def create_user():
    """
    Creates the user and stores their tokens and current user in a session variable. If the user just logged in, callbacks to Coinbase to create the user. If the user has already logged in, creates the user from the tokens session variables.
    
    return: the user 
            or, a redirect to the Coinbase login if there were errors
    """
    if 'tokens' in session: # If the tokens session variable exists ...
        if datetime.now() - session['tokens_created_at'] > timedelta(hours=1): # If the user's tokens are about to expire ...
            session.pop('tokens', None) # delete the tokens session variable ...
            session.pop('tokens_created_at', None)
            session.pop('current_user', None) # delete the current user session variable ...
            session.pop('payment_methods', None) # delete the payment methods session variable ...
            return connect.coinbase_login() # and redirect the user to login.
        else:
            if 'payment_methods' in session and 'current_user' in session: # If the payment methods and current user session variables exist ...
                user = User(tokens=session['tokens'],  payment_methods=session['payment_methods'], current_user=session['current_user']) # create the user using them.
            elif 'current_user' in session: # If only the current user session variable exists ...
                user = User(tokens=session['tokens'], current_user=session['current_user']) # create the user using it only.
            else:
                user = User(tokens=session['tokens'])
            
            return user

    else:
        try: # If the user has just logged in ...
            tokens = connect.coinbase_callback() # callback to Coinbase to get the tokens ...
            session['tokens'] = tokens # and store the tokens in a session variable.
            session['tokens_created_at'] = datetime.now()

            user = User(tokens) # Create the user.

            session['current_user'] = user.current_user # Store the user's information in a session variable.
            if hasattr(user, 'bank_payment_method_id'): # If the user has a bank payment method ...
                session['payment_methods'] = user.payment_methods # store the user's payment methods in a session variable.

            return user

        except: # If the user has not logged in or their tokens have expired ...
            return connect.coinbase_login() # redirect them to login.

def get_basket_names():
    """Gets the names of all baskets in the database."""
    #baskets = BasketModel.query.All()
    #basket_names = []

	#for basket in baskets:
	#	basket_names.append(basket.name)

    #return basket_names

    return ['Default Basket']

