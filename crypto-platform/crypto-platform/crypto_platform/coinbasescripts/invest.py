"""
Scripts for initial investing and tax-loss harvesting.
"""

import uuid
from flask import redirect, request
import requests
import json
import time

possible_basket = [['BTC', 0.5], ['ETH', 0.5]] # I think the baskets are best represented as lists in the code. When we set up the database, we can put the data into a list like this.
another_possible_basket = [['BTC', 0.4], ['ETH', 0.2], ['USDT', 0.2], ['BNB', 0.2]]

def make_initial_investment(user, basket, amount):
    """Makes the user's initial investment."""
    pass

def check_tax_loss_harvest(): # This is the function that we would run periodically to determine if we will send a notification to our users
    """Checks potential for tax-loss harvesting."""
    pass

def tax_loss_harvest(user): # This is the function that would run everytime the user activates it. Either by clicking a button, logging in, or withdrawing their investment.
    """Performs the tax-loss harvesting process."""

    # IMPORTANT
    # After you sell but before you buy, make sure to check that user.cash_payment_method[primary_buy] == True
    # Also, be sure to buy the exact amount in the Cash wallet, no more no less
    # This ensures that the buys will be paid for by the earnings from the sells and NOT the user's added payment method

    pass

def get_crypto_prices(): # This is the function that will get the prices of every crypto currency
    response = requests.get('https://api.coinbase.com/v2/prices/BTC-USD/spot')
    data = response.json()
    BTC_price = data["data"]["amount"]
    response = requests.get('https://api.coinbase.com/v2/prices/ETH-USD/spot')
    data = response.json()
    ETH_price = data["data"]["amount"]
    crypto_prices = [['BTC', BTC_price], ['ETH', ETH_price]]
    return crypto_prices

def get_one_price(crypto_prices, crypto):
    for price in crypto_prices:
        if (price[0] == crypto):
            return price[1]

def process_investments():
    investing = True
    crypto_prices = get_crypto_prices()
    BTC_price = get_one_price(crypto_prices, 'BTC')
    print (crypto_prices)
    print (BTC_price)

