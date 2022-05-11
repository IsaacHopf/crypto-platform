"""
Routes and views for the dashboard pages.
"""

from flask import Flask, Blueprint, render_template, session, request, flash
from datetime import datetime, timedelta
import time
import re

from crypto_platform import connect
from crypto_platform.dashboard import transact, taxlossharvest
from crypto_platform.dashboard.User import User

# For the Database
from crypto_platform.models import UserModel, BasketModel, BasketCryptoPercentageModel, UserBasketModel, UserBasketCryptoAmountModel, FailedBuyModel, FailedSellModel

dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard', 
                      template_folder='templates',
                      static_folder='static')

@dashboard.route('/')
def home():
    """Handles the callback to Coinbase and renders the Dashboard page."""
    try:
        user = create_user()
    except:
        return connect.coinbase_login()

    return render_template(
        'dashboard.html',
        cash_wallet_balance = user.get_cash_wallet_balance(),
        user_basket_balances = get_user_basket_balances(user),
        native_currency = user.native_currency,
        basket_names = get_basket_names(),
        failed_buys_basket_names = get_failed_buys_basket_names(user),
        failed_sells_basket_names = get_failed_sells_basket_names(user),
        showTaxLossHarvestForm = "False",
        step_one_visibility = '',
        step_two_visibility = 'hidden'
    )

@dashboard.route('/deposit', methods=['POST'])
def deposit():
    """Handles depositing funds into the user's Cash Wallet."""
    try:
        user = create_user()
    except:
        return connect.coinbase_login()

    try:
        deposit_amount = float(request.form['deposit-amount'])
    except:

        return render_template(
            'dashboard.html',
            cash_wallet_balance = user.get_cash_wallet_balance(),
            user_basket_balances = get_user_basket_balances(user),
            native_currency = user.native_currency,
            basket_names = get_basket_names(),
            failed_buys_basket_names = get_failed_buys_basket_names(user),
            failed_sells_basket_names = get_failed_sells_basket_names(user),
            step_one_visibility = '',
            step_two_visibility = 'hidden'
        )
    else:

        if re.match("^\d*", str(deposit_amount)): # If the deposit amount exists and is a number ...
            if deposit_amount >= 10:
                transact.deposit(user, deposit_amount) # make the deposit.
            else:
                flash('Whoops! Depsoit amount must be greater than or equal to 10.', 'error')

        return render_template(
            'dashboard.html',
            cash_wallet_balance = user.get_cash_wallet_balance(),
            user_basket_balances = get_user_basket_balances(user),
            native_currency = user.native_currency,
            basket_names = get_basket_names(),
            failed_buys_basket_names = get_failed_buys_basket_names(user),
            failed_sells_basket_names = get_failed_sells_basket_names(user),
            step_one_visibility = '',
            step_two_visibility = 'hidden'
        )

@dashboard.route('/buybasket', methods=['POST'])
def buybasket():
    """Handles buying a basket."""
    try:
        user = create_user()
    except:
        return connect.coinbase_login()

    try:
        selected_basket_name = request.form['basket-to-buy']
        invest_amount = float(request.form['invest-amount'])
    except:
        return render_template(
            'dashboard.html',
            cash_wallet_balance = user.get_cash_wallet_balance(),
            user_basket_balances = get_user_basket_balances(user),
            native_currency = user.native_currency,
            basket_names = get_basket_names(),
            failed_buys_basket_names = get_failed_buys_basket_names(user),
            failed_sells_basket_names = get_failed_sells_basket_names(user),
            step_one_visibility = '',
            step_two_visibility = 'hidden'
        )
    else:

        if re.match("^\d*", str(invest_amount)): # If the selected basket name and invest amount exist and if the invest amount is a number ...
            if invest_amount >= 10:
                transact.buy_basket(user, selected_basket_name, invest_amount) # make the investment.
            else:
                flash('Whoops! Invest amount must be greater than or equal to 10.', 'error')

        return render_template(
            'dashboard.html',
            cash_wallet_balance = user.get_cash_wallet_balance(),
            user_basket_balances = get_user_basket_balances(user),
            native_currency = user.native_currency,
            basket_names = get_basket_names(),
            failed_buys_basket_names = get_failed_buys_basket_names(user),
            failed_sells_basket_names = get_failed_sells_basket_names(user),
            step_one_visibility = '',
            step_two_visibility = 'hidden'
        )

@dashboard.route('/sellbasket', methods=['POST'])
def sellbasket():
    """Handles selling a basket."""
    try:
        user = create_user()
    except:
        return connect.coinbase_login()

    try:
        selected_basket_name = request.form['basket-to-sell']
    except:
        return render_template(
            'dashboard.html',
            cash_wallet_balance = user.get_cash_wallet_balance(),
            user_basket_balances = get_user_basket_balances(user),
            native_currency = user.native_currency,
            basket_names = get_basket_names(),
            failed_buys_basket_names = get_failed_buys_basket_names(user),
            failed_sells_basket_names = get_failed_sells_basket_names(user),
            step_one_visibility = '',
            step_two_visibility = 'hidden'
        )
    else:

        transact.sell_basket(user, selected_basket_name)

        return render_template(
            'dashboard.html',
            cash_wallet_balance = user.get_cash_wallet_balance(),
            user_basket_balances = get_user_basket_balances(user),
            native_currency = user.native_currency,
            basket_names = get_basket_names(),
            failed_buys_basket_names = get_failed_buys_basket_names(user),
            failed_sells_basket_names = get_failed_sells_basket_names(user),
            step_one_visibility = '',
            step_two_visibility = 'hidden'
        )

@dashboard.route('/withdraw', methods=['POST'])
def withdraw():
    """Handles withdrawing."""
    try:
        user = create_user()
    except:
        return connect.coinbase_login()

    try:
        withdraw_amount = float(request.form['withdraw-amount'])
    except:
        return render_template(
            'dashboard.html',
            cash_wallet_balance = user.get_cash_wallet_balance(),
            user_basket_balances = get_user_basket_balances(user),
            native_currency = user.native_currency,
            basket_names = get_basket_names(),
            failed_buys_basket_names = get_failed_buys_basket_names(user),
            failed_sells_basket_names = get_failed_sells_basket_names(user),
            step_one_visibility = '',
            step_two_visibility = 'hidden'
        )
    else:

        if re.match("^\d*", str(withdraw_amount)): # If the withdraw amount exists and is a number ...
            transact.withdraw(user, withdraw_amount) # make the withdraw.

        return render_template(
            'dashboard.html',
            cash_wallet_balance = user.get_cash_wallet_balance(),
            user_basket_balances = get_user_basket_balances(user),
            native_currency = user.native_currency,
            basket_names = get_basket_names(),
            failed_buys_basket_names = get_failed_buys_basket_names(user),
            failed_sells_basket_names = get_failed_sells_basket_names(user),
            step_one_visibility = '',
            step_two_visibility = 'hidden'
        )


#@dashboard.route('/testscripts')
#def testscripts():
#    try:
#        user = create_user()
#    except:
#        return connect.coinbase_login()

#    taxlossharvest.process_investments(user)

#    return render_template(
#        'dashboard.html',
#        cash_wallet_balance = user.get_cash_wallet_balance(),
#        user_basket_balances = get_user_basket_balances(user),
#        native_currency = user.native_currency,
#        basket_names = get_basket_names(),
#        step_one_visibility = '',
#        step_two_visibility = 'hidden'
#    )

@dashboard.route('/taxlossharvestcheck', methods=['POST'])
def taxlossharvestcheck():
    try:
        user = create_user()
    except:
        return connect.coinbase_login()


    #data = taxlossharvest.process_investments(user)

    return render_template(
        'dashboard.html',
        cash_wallet_balance = user.get_cash_wallet_balance(),
        user_basket_balances = get_user_basket_balances(user),
        native_currency = user.native_currency,
        basket_names = get_basket_names(),
        data = taxlossharvest.use_test_data(user),
        step_one_visibility = 'hidden',
        step_two_visibility = ''
    )

@dashboard.route('/taxlossharvestconfirm', methods=['POST'])
def taxlossharvestconfirm():
    try:
        user = create_user()
    except:
        return connect.coinbase_login()


    #data = taxlossharvest.process_investments(user)

    return render_template(
        'dashboard.html',
        cash_wallet_balance = user.get_cash_wallet_balance(),
        user_basket_balances = get_user_basket_balances(user),
        native_currency = user.native_currency,
        basket_names = get_basket_names(),
        data = taxlossharvest.use_test_data(user),
        showTaxLossHarvestConfirmForm = "True",
        step_one_visibility = 'hidden',
        step_two_visibility = ''
    )

@dashboard.route('/taxlossharvestprocess', methods=['POST'])
def taxlossharvestprocess():
    try:
        user = create_user()
    except:
        return connect.coinbase_login()


    #taxlossharvest.perform_harvest_sells(user,data)

    return render_template(
        'dashboard.html',
        cash_wallet_balance = user.get_cash_wallet_balance(),
        user_basket_balances = get_user_basket_balances(user),
        native_currency = user.native_currency,
        basket_names = get_basket_names(),
        showTaxLossHarvestConfirmForm = "False",
        step_one_visibility = 'hidden',
        step_two_visibility = ''
    )

@dashboard.route('/testharvest')
def testharvest():
    try:
        user = create_user()
    except:
        return connect.coinbase_login()

    data = taxlossharvest.use_test_data(user)

    return render_template(
        'dashboard.html',
        cash_wallet_balance = user.get_cash_wallet_balance(),
        user_basket_balances = get_user_basket_balances(user),
        native_currency = user.native_currency,
        basket_names = get_basket_names(),
        data=data,
        step_one_visibility = 'hidden',
        step_two_visibility = ''
    )

@dashboard.route('/retrybuys', methods=['POST'])
def retrybuys():
    try:
        user = create_user()
    except:
        return connect.coinbase_login()

    try:
        selected_basket_name = request.form['basket-to-retry-buying']
    except:
        return render_template(
            'dashboard.html',
            cash_wallet_balance = user.get_cash_wallet_balance(),
            user_basket_balances = get_user_basket_balances(user),
            native_currency = user.native_currency,
            basket_names = get_basket_names(),
            failed_buys_basket_names = get_failed_buys_basket_names(user),
            failed_sells_basket_names = get_failed_sells_basket_names(user),
            step_one_visibility = '',
            step_two_visibility = 'hidden'
        )
    else:

        transact.retry_buy_basket(user, selected_basket_name)

        return render_template(
            'dashboard.html',
            cash_wallet_balance = user.get_cash_wallet_balance(),
            user_basket_balances = get_user_basket_balances(user),
            native_currency = user.native_currency,
            basket_names = get_basket_names(),
            failed_buys_basket_names = get_failed_buys_basket_names(user),
            failed_sells_basket_names = get_failed_sells_basket_names(user),
            step_one_visibility = '',
            step_two_visibility = 'hidden'
        )

@dashboard.route('/retrysells', methods=['POST'])
def retrysells():
    try:
        user = create_user()
    except:
        return connect.coinbase_login()

    try:
        selected_basket_name = request.form['basket-to-retry-selling']
    except:
        return render_template(
            'dashboard.html',
            cash_wallet_balance = user.get_cash_wallet_balance(),
            user_basket_balances = get_user_basket_balances(user),
            native_currency = user.native_currency,
            basket_names = get_basket_names(),
            failed_buys_basket_names = get_failed_buys_basket_names(user),
            failed_sells_basket_names = get_failed_sells_basket_names(user),
            step_one_visibility = '',
            step_two_visibility = 'hidden'
        )
    else:

        transact.retry_sell_basket(user, selected_basket_name)

        return render_template(
            'dashboard.html',
            cash_wallet_balance = user.get_cash_wallet_balance(),
            user_basket_balances = get_user_basket_balances(user),
            native_currency = user.native_currency,
            basket_names = get_basket_names(),
            failed_buys_basket_names = get_failed_buys_basket_names(user),
            failed_sells_basket_names = get_failed_sells_basket_names(user),
            step_one_visibility = '',
            step_two_visibility = 'hidden'
        )

def create_user():
    """
    Creates the user and stores their tokens, user information, and payment methods in a session variable. If the user just logged in, callbacks to Coinbase to create the user. If the user has already logged in, creates the user from the session variables.
    
    return: the user, represented as an object of the User class
    """
    if 'tokens' in session: # If the tokens session variable exists ...
        if datetime.now() - session['tokens_created_at'] > timedelta(hours=1): # If the user's tokens are about to expire ...
            session.pop('tokens', None) # delete the tokens session variable ...
            session.pop('tokens_created_at', None)
            session.pop('current_user', None) # delete the current user session variable ...
            session.pop('payment_methods', None) # delete the payment methods session variable ...
            raise Exception('LoginRequired') # and raise exception.

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
            raise Exception('LoginRequired') # and raise exception.

def get_basket_names():
    """Gets the names of all baskets in the database."""
    basket_names = []

    baskets = BasketModel.get_all()

    for basket in baskets:
        basket_names.append(basket.name)

    return basket_names

def get_failed_buys_basket_names(user):
    """Gets the basket names of the user's failed buys."""
    basket_names = []

    failed_buys = FailedBuyModel.get_all_by_user(user)

    if failed_buys:
        for failed_buy in failed_buys:
            basket = BasketModel.get_by_id(failed_buy.basket_id)
            if basket.name not in basket_names:
                basket_names.append(basket.name)

        flash('Oh no! Some of your buys did not process.', 'failedbuyerror')

    return basket_names

def get_failed_sells_basket_names(user):
    """Gets the basket names of the user's failed sells."""
    basket_names = []

    failed_sells = FailedSellModel.get_all_by_user(user)

    if failed_sells:
        for failed_sell in failed_sells:
            basket = BasketModel.get_by_id(failed_sell.basket_id)
            if basket.name not in basket_names:
                basket_names.append(basket.name)

        flash('Oh no! Some of your sells did not process.', 'failedsellerror')

    return basket_names

def get_user_basket_balances(user):
    user_basket_balances = []

    user_baskets = UserBasketModel.get_all_by_user(user)

    for user_basket in user_baskets:
        basket = BasketModel.get_by_id(user_basket.basket_id)
        basket_name = basket.name
        user_basket_crypto_amounts = UserBasketCryptoAmountModel.get_all_by_user_and_basket(user, basket)

        basket_balance = 0

        for user_basket_crypto_amount in user_basket_crypto_amounts:
            crypto = user_basket_crypto_amount.crypto # The cryptocurrency.
            bought_amount = user_basket_crypto_amount.amount # The amount of this cryptocurrency originally bought.
            user_crypto_amounts = UserBasketCryptoAmountModel.get_all_by_user_and_crypto(user, crypto)
            total_bought_amount = 0

            for user_crypto_amount in user_crypto_amounts: # For all of the user's user_basket_crypto_amounts with the same cryptocurrency ...
                total_bought_amount += user_crypto_amount.amount # add their originally bought amounts to the total amount.

            current_balance = user.get_crypto_wallet_balance_in_native_currency(crypto) # Get the current balance of the specified cryptocurrency wallet.
            crypto_balance = (bought_amount / total_bought_amount) * current_balance # Calculate the current balance of for this crypto in this basket.

            basket_balance += crypto_balance

        user_basket_balances.append([basket_name, round(basket_balance, 2)])

    return user_basket_balances


            

