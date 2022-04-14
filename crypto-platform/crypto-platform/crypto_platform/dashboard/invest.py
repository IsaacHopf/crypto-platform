"""
Scripts for investing and withdrawing.
"""
from flask import flash
from crypto_platform.dashboard.User import User
import time

# For the Database
from crypto_platform import db
from crypto_platform.models import FailedBuyModel, FailedSellModel

# deposit money into cash wallet

# buy basket using cash wallet

# sell basket, put funds in cash wallet

# withdraw money from cash wallet

def make_investment(user, basket, invested_amount):
    """
    Makes the user's investment for a selected basket.

    user: the user, represented as an object of the User class
    basket: the user's selected basket, represented as a list of lists of crypto percentages that add up to 1 (Ex. [['BTC', 0.5], ['ETH', 0.5]])
    amount: the amount to invest for the selected basket (in the user's native currency)
    """
    num_buys = 0
    num_failed_buys = 0
    last_error = ''

    for crypto_percentage in basket:
        crypto = crypto_percentage[0] # The cryptocurrency.
        percent = crypto_percentage[1] # The percentage this cryptocurrency makes up in the basket.
        buy_amount = invested_amount * percent # The amount of this cryptocurrency to buy.

        num_buys += 1

        try:
            user.buy_with_bank_payment_method(crypto, buy_amount)

        except Exception as e:
            num_failed_buys += 1
            last_error = str(e)

            failed_buy = FailedBuyModel(
                user_id = user.coinbase_id,
                crypto = crypto,
                buy_amount = buy_amount)

            db.session.add(failed_buy)
            db.session.commit()

    if num_failed_buys > 0:
        flash('Oh no! {} of your {} buys did not process, please retry in an hour. Error Code: {}'.format(num_failed_buys, num_buys, last_error), 'error')
    else:
        flash('Your buys processed successfully! You should receive several emails from Coinbase.')

def retry_make_investment(user):
    """
    Retries all of the user's failed buys.

    user: the user, represented as an object of the User class
    """
    num_buys = 0
    num_failed_buys = 0
    last_error = ''
    failed_buys = FailedBuyModel.query.filter_by(user_id = user.coinbase_id).all()

    for failed_buy in failed_buys:
        crypto = failed_buy.crypto
        buy_amount = failed_buy.buy_amount

        num_buys += 1

        try:
            user.buy_with_bank_payment_method(crypto, buy_amount)

        except Exception as e:
            num_failed_buys += 1
            last_error = str(e)
        else:
            db.session.delete(failed_buy)
            db.session.commit()

    if num_failed_buys > 0:
        flash('Oh no! {} of your {} buys did not process, please retry in an hour. Error Code: {}'.format(num_failed_buys, num_buys, last_error), 'error')
    else:
        flash('Your buys processed successfully! You should receive several emails from Coinbase.')


def make_withdrawal(user, basket, invested_amount):
    """
    Makes the user's withdrawal for a selected basket.

    user: the user, represented as an object of the User class
    basket: the user's selected basket, represented as a list of lists of crypto percentages that add up to 1 (Ex. [['BTC', 0.5], ['ETH', 0.5]])
    invested_amount: the amount to invest for the selected basket (in the user's native currency)
    """
    #check cash wallet
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

            failed_sell = FailedSellModel(
                user_id = user.coinbase_id,
                crypto = crypto,
                sell_amount = sell_amount)

            db.session.add(failed_sell)
            db.session.commit()

    if num_failed_sells > 0:
        flash('Oh no! {} of your {} sells did not process, please retry in an hour. Error Code: {}'.format(num_failed_sells, num_sells, last_error), 'error')     
    else:
        flash('Your sells processed successfully! You should receive several emails from Coinbase.')
        time.sleep(60) # Wait for a minute (NOT A SECURE SOLUTION)
        # check cash wallet
        # while 
        # if they don't have cash yet, try again in a few seconds
        user.withdraw(user.get_cash_wallet_balance())
        #flash('Your withdrawal has been processed! You should recieve several emails from Coinbase.')

def retry_make_withdrawal(user):
    """
    Retries all the user's failed sells.

    user: the user, represented as an object of the User class
    """
    #check cash wallet
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
        flash('Your sells processed successfully! You should receive several emails from Coinbase.')
        time.sleep(60) # Wait for a minute (NOT A SECURE SOLUTION)
        # check cash wallet
        # while 
        # if they don't have cash yet, try again in a few seconds
        user.withdraw(user.get_cash_wallet_balance())
        #flash('Your withdrawal has been processed! You should recieve several emails from Coinbase.')


    