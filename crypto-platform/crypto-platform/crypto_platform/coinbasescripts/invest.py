"""
Scripts for initial investing and tax-loss harvesting.
"""
import uuid
from flask import redirect, request
import requests
import json
import time
from crypto_platform.coinbasescripts.User import User
from crypto_platform import views

possible_basket = [['BTC', 0.5], ['ETH', 0.5]] # I think the baskets are best represented as lists in the code. When we set up the database, we can put the data into a list like this.
another_possible_basket = [['BTC', 0.4], ['ETH', 0.2], ['USDT', 0.2], ['YFI', 0.2]]


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

        user.buy_with_bank_payment_method(crypto, crypto_amount)

def check_tax_loss_harvest(): # This is the function that we would run periodically to determine if we will send a notification to our users
    """Checks potential for tax-loss harvesting."""
    pass

def tax_loss_harvest(user): # This is the function that would run everytime the user activates it. Either by clicking a button, logging in, or withdrawing their investment.
    """Performs the tax-loss harvesting process."""

    # After selling but before buying more, make sure to check that the user's cash wallet received the earnings from selling by calling user.get_cash_wallet_balance()
    # Also, be sure to use user.buy_with_cash_payment_method() when buying

    pass

def get_all_crypto_prices(): # This is the function that will get the prices of every crypto currency we use

    all_crypto_prices = [['BTC', 0], ['ETH', 0], ['USDT', 0], ['LTC', 0]] #This list will contain every crypto we use and its price.

    for crypto in all_crypto_prices: #Gets the price of every crypto by calling get_one_price for every crypto and saving the price.
        price = get_one_price(crypto[0])
        crypto[1] = price
    return all_crypto_prices

def get_one_price(crypto): #This function will get the price of one crypto currency and return that price.
    request_url = ("https://api.coinbase.com/v2/prices/" + crypto + "-USD/spot") #URL for specific crypto
    response = requests.get(request_url)
    data = response.json()
    price = data["data"]["amount"] #price of the crypto
    return price

def get_spot_price(crypto, date, user):
    spot_price = user.client.get_spot_price(currency_pair= 'BTC-USD', date='2022-3-2')
    return spot_price

"""def get_one_price(crypto_prices, crypto):
    for price in crypto_prices:
        if (price[0] == crypto):
            return price[1]"""

def process_investments(user):
    investing = True
    all_crypto_prices = get_all_crypto_prices()
    spot_price = get_spot_price('BTC', '2022-3-2', user)
    print (f"the spot price is {spot_price}")
    print (all_crypto_prices)

