"""
Scripts for investing and withdrawing.
"""
from flask import flash
from crypto_platform.dashboard.User import User

def make_initial_investment(user, basket, amount):
    """
    Makes the user's initial investment for a selected basket.

    user: the user, represented as an object of the User class
    basket: the user's selected basket, represented as a list of lists of crypto percentages that add up to 1 (Ex. [['BTC', 0.5], ['ETH', 0.5]])
    amount: the amount to invest for the selected basket (in the user's native currency)
    """
    for crypto_percentage in basket:
        crypto = crypto_percentage[0] # The cryptocurrency.
        percent = crypto_percentage[1] # The percentage this cryptocurrency makes up in the basket.
        crypto_amount = amount * percent # The amount of this cryptocurrency to buy.

        #user.test_buy(crypto, crypto_amount)
        user.buy_with_bank_payment_method(crypto, crypto_amount)
    flash('Your investment has been processed! You should recieve several emails from Coinbase.')
