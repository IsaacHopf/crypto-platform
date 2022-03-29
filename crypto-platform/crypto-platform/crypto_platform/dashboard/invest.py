"""
Scripts for initial investing and tax-loss harvesting.
"""
import uuid
from flask import redirect, request
import requests
import json
import time
from crypto_platform.dashboard.User import User
from datetime import date
from datetime import timedelta

all_crypto_prices = [['BTC', 0], ['ETH', 0], ['USDT', 0], ['LTC', 0]] #This list will contain every crypto we use and its price
potential_harvest_dates = []
user_buys = []

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

def check_tax_loss_harvest(all_crypto_prices, user): # This is the function that we would run periodically to determine if we will send a notification to our users
    """Checks potential for tax-loss harvesting."""
    today = date.today()
    threshold = -0.1
    print("Today is: ", today)

    for crypto_price in all_crypto_prices: #loop through every currency
        print (f"the current price today for {crypto_price[0]} is {crypto_price[1]}")
        for i in range(365): #loop through the previous year
            loop_day = today - timedelta(days = i)
            spot_price = get_spot_price(crypto_price[0]+'-USD', loop_day, user)
            amount = float(spot_price["amount"])
            print (f"the spot price was {amount} on {loop_day}")
            change_in_price = float(crypto_price[1]) - (amount) 
            print (f"the change in price was: {change_in_price}")
            if ((change_in_price/amount) <= threshold):
                print ("there is potential for harvesting")
                potential_harvest_dates.append([crypto_price[0], loop_day])
    print ("............................................")
    print ("These are the days with potential to harvest:")
    print (potential_harvest_dates)

def verify_tax_loss_harvest(user):
    all_buys = user.client.get_buys(user.client.get_account('BTC')['id'])
    for buy in all_buys["data"]:

        date = buy["created_at"]
        amount = buy["amount"]
        print (amount)
        unit_price = buy["unit_price"]["amount"]
        user_buys.append(['BTC', date, amount, unit_price])
    print (user_buys)

def tax_loss_harvest(user): # This is the function that would run everytime the user activates it. Either by clicking a button, logging in, or withdrawing their investment.
    """Performs the tax-loss harvesting process."""

    # After selling but before buying more, make sure to check that the user's cash wallet received the earnings from selling by calling user.get_cash_wallet_balance()
    # Also, be sure to use user.buy_with_cash_payment_method() when buying

    pass

def get_all_crypto_prices(): # This is the function that will get the prices of every crypto currency we use

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

def get_spot_price(currency_pair, date, user): #currency_pair must be in format like 'BTC-USD' and date must be in format like '2022-3-2'
    spot_price = user.client.get_spot_price(currency_pair=currency_pair, date=date)
    return spot_price
        

def process_investments(user):
    investing = True
    all_crypto_prices = get_all_crypto_prices()
    spot_price = get_spot_price('BTC-USD', '2022-3-2', user)
    print (f"the spot price is {spot_price}")
    print (all_crypto_prices)
    verify_tax_loss_harvest(user)
    time.sleep(30)
    check_tax_loss_harvest(all_crypto_prices, user)