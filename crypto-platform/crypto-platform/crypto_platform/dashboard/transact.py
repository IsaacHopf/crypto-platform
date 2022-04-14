"""
Scripts for transactions (deposit, buy, sell, withdraw).
"""
from flask import flash
from crypto_platform.dashboard.User import User
import time

# For the Database
from crypto_platform.models import FailedBuyModel, FailedSellModel
from crypto_platform import db

def deposit(user, amount):
    """Deposits funds for the user."""
    try:
        user.deposit(amount)
    except Exception as e:
        flash('Oh no! Your deposit did not process, please try again in an hour. Error Code: ' + str(e), 'error')
    else:
        flash('Your deposit processed successfully! You should receive an email from Coinbase.', 'success')

def buy_basket(user, basket, invest_amount):
    """
    Buys a basket for the user.

    user: the user, represented as an object of the User class
    basket: the user's selected basket, represented as a list of lists of crypto percentages that add up to 1 (Ex. [['BTC', 0.5], ['ETH', 0.5]])
    invest_amount: the amount to invest for the selected basket (in the user's native currency)
    """
    if user.get_cash_wallet_balance() < invest_amount:
        flash('Oh no! You do not have enough funds to invest. Please deposit more funds before buying.', 'error')
    else:
        num_buys = 0
        num_failed_buys = 0
        last_error = ''

        for crypto_percentage in basket:
            crypto = crypto_percentage[0] # The cryptocurrency.
            percent = crypto_percentage[1] # The percentage this cryptocurrency makes up in the basket.
            buy_amount = invest_amount * percent # The amount of this cryptocurrency to buy.

            num_buys += 1

            try:
                user.buy(crypto, buy_amount)

            except Exception as e:
                num_failed_buys += 1
                last_error = str(e)

                failed_buy = FailedBuyModel(user_id = user.coinbase_id,
                                            crypto = crypto,
                                            buy_amount = buy_amount)

                db.session.add(failed_buy)
                db.session.commit()

        if num_failed_buys > 0:
            flash('Oh no! {} of your {} buys did not process, please retry in an hour. Error Code: {}'.format(num_failed_buys, num_buys, last_error), 'error')
        else:
            flash('Your buys processed successfully! You should receive several emails from Coinbase.', 'success')

def retry_buy_basket(user):
    """
    Retries buying all of the user's failed buys.

    user: the user, represented as an object of the User class
    """
    if user.get_cash_wallet_balance() < invest_amount:
        flash('Oh no! You do not have enough funds to invest. Please deposit more funds before buying.', 'error')
    else:
        num_buys = 0
        num_failed_buys = 0
        last_error = ''
        failed_buys = FailedBuyModel.query.filter_by(user_id = user.coinbase_id).all()

        for failed_buy in failed_buys:
            crypto = failed_buy.crypto
            buy_amount = failed_buy.buy_amount

            num_buys += 1

            try:
                user.buy(crypto, buy_amount)

            except Exception as e:
                num_failed_buys += 1
                last_error = str(e)
            else:
                db.session.delete(failed_buy)
                db.session.commit()

        if num_failed_buys > 0:
            flash('Oh no! {} of your {} buys did not process, please retry in an hour. Error Code: {}'.format(num_failed_buys, num_buys, last_error), 'error')
        else:
            flash('Your buys processed successfully! You should receive several emails from Coinbase.', 'success')

def sell_basket(user, basket, invested_amount):
    """
    Sells a basket for the user.

    user: the user, represented as an object of the User class
    basket: the user's selected basket, represented as a list of lists of crypto percentages that add up to 1 (Ex. [['BTC', 0.5], ['ETH', 0.5]])
    invested_amount: the amount to invest for the selected basket (in the user's native currency)
    """
    num_sells = 0
    num_failed_sells = 0
    last_error = ''

    for crypto_percentage in basket:
        crypto = crypto_percentage[0] # The cryptocurrency.
        percent = crypto_percentage[1] # The percentage this cryptocurrency makes up in the basket.
        sell_amount = invested_amount * percent # The amount of this cryptocurrency to sell.

        num_sells += 1

        try:
            user.sell(crypto, sell_amount)

        except Exception as e:
            num_failed_sells += 1
            last_error = str(e)

            failed_sell = FailedSellModel(user_id = user.coinbase_id,
                                          crypto = crypto,
                                          sell_amount = sell_amount)

            db.session.add(failed_sell)
            db.session.commit()

    if num_failed_sells > 0:
        flash('Oh no! {} of your {} sells did not process, please retry in an hour. Error Code: {}'.format(num_failed_sells, num_sells, last_error), 'error')     
    else:
        flash('Your sells processed successfully! You should receive several emails from Coinbase.', 'success')

def retry_sell_basket(user):
    """
    Retries selling all the user's failed sells.

    user: the user, represented as an object of the User class
    """
    num_sells = 0
    num_failed_sells = 0
    last_error = ''
    failed_sells = FailedSellModel.query.filter_by(user_id = user.coinbase_id).all()

    for failed_sell in failed_sells:
        crypto = failed_sell.crypto
        sell_amount = failed_sell.sell_amount

        num_sells += 1

        try:
            user.sell(crypto, sell_amount)

        except Exception as e:
            num_failed_sells += 1
            last_error = str(e)
        else:
            db.session.delete(failed_sell)
            db.session.commit()

    if num_failed_sells > 0:
        flash('Oh no! {} of your {} sells did not process, please retry in an hour. Error Code: {}'.format(num_failed_sells, num_sells, last_error), 'error')     
    else:
        flash('Your sells processed successfully! You should receive several emails from Coinbase.', 'success')

def withdraw(user, amount):
    """Withdraws funds for the user."""
    if user.get_cash_wallet_balance() < amount:
        flash('Oh no! You cannot withdraw that much. Please withdraw less funds or sell a basket.', 'error')
    else:
        try:
            user.withdraw(amount)
        except Exception as e:
            flash('Oh no! Your withdraw did not process, please try again in an hour. Error Code: ' + str(e), 'error')
        else:
            flash('Your withdraw processed successfully! You should receive an email from Coinbase.', 'success')


    