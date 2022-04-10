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
    create_user()

    return render_template(
        'dashboard.html',
        title='Dashboard',
        #year=datetime.now().year,
        message='Your application description page.',
        baskets=get_basket_names(),
        step_one_visibility = '',
        step_two_visibility = 'hidden'
    )

@dashboard.route('/selectbasket', methods=['POST'])
def selectbasket():
    """Handles selecting a basket and investing."""
    create_user()

    selected_basket_name = request.form['baskets']
    investment_amount = float(request.form['investment-amount'])

    #selected_basket = BasketModel.query.filter_by(name='selected_basket')
    #get crypto percentages
    
    selected_basket = [['BTC', 0.4], ['ETH', 0.3], ['LTC', 0.2], ['ADA', 0.1]]

    invest.make_initial_investment(user, selected_basket, investment_amount)

    return render_template(
        'dashboard.html',
        title='Dashboard',
        #year=datetime.now().year,
        message='Your application description page.',
        baskets=get_basket_names(),
        step_one_visibility = '',
        step_two_visibility = 'hidden'
    )


@dashboard.route('/testscripts')
def testscripts():
    invest.process_investments(user)

    return render_template(
        'dashboard.html',
        title='Dashboard',
        year=datetime.now().year,
        baskets=get_basket_names(),
        step_one_visibility = '',
        step_two_visibility = 'hidden'
    )

@dashboard.route('/checkharvest')
def checkharvest():
    create_user()

    data = invest.process_investments(user)

    return render_template(
        'dashboard.html',
        title='Dashboard',
        #year=datetime.now().year,
        baskets=get_basket_names(),
        data=data,
        step_one_visibility = 'hidden',
        step_two_visibility = ''
    )

def create_user():
    """Handles the callback to Coinbase and creates the User."""
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

def get_basket_names():
    """Gets the names of all baskets in the database."""
    #baskets = BasketModel.query.All()
    #basket_names = []

	#for basket in baskets:
	#	basket_names.append(basket.name)

    #return basket_names

    return ['Default Basket']

