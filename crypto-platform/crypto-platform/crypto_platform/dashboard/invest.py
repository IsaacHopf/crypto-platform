"""
Scripts for investing and withdrawing.
"""
from flask import flash
from crypto_platform.dashboard.User import User
import time

def make_investment(user, basket, invested_amount):
    """
    Makes the user's investment for a selected basket.

    user: the user, represented as an object of the User class
    basket: the user's selected basket, represented as a list of lists of crypto percentages that add up to 1 (Ex. [['BTC', 0.5], ['ETH', 0.5]])
    amount: the amount to invest for the selected basket (in the user's native currency)
    """
    for crypto_percentage in basket:
        crypto = crypto_percentage[0] # The cryptocurrency.
        percent = crypto_percentage[1] # The percentage this cryptocurrency makes up in the basket.
        buy_amount = invested_amount * percent # The amount of this cryptocurrency to buy.

        #user.test_buy(crypto, buy_amount)
        user.buy_with_bank_payment_method(crypto, buy_amount)
    flash('Your investment has been processed! You should recieve several emails from Coinbase.')

def make_withdrawal(user, basket, invested_amount):
    """
    Makes the user's withdrawal for a selected basket.

    user: the user, represented as an object of the User class
    basket: the user's selected basket, represented as a list of lists of crypto percentages that add up to 1 (Ex. [['BTC', 0.5], ['ETH', 0.5]])
    invested_amount: the amount to invest for the selected basket (in the user's native currency)
    """
    for crypto_percentage in basket:
        crypto = crypto_percentage[0] # The cryptocurrency.
        percent = crypto_percentage[1] # The percentage this cryptocurrency makes up in the basket.
        sell_amount = invested_amount * percent # The amount of this cryptocurrency to sell.

        user.sell(crypto, sell_amount)

    time.sleep(60) # Wait for a minute (NOT A SECURE SOLUTION)
    user.withdraw(user.get_cash_wallet_balance())
    flash('Your withdrawal has been processed! You should recieve several emails from Coinbase.')