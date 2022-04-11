"""
Scripts for tax-loss harvesting.
"""
import uuid
from flask import redirect, request
import requests
import json
import time
import datetime
import re
from crypto_platform.dashboard.User import User
from datetime import date
from datetime import timedelta

all_crypto_prices = [['BTC', 0], ['ETH', 0], ['USDT', 0], ['LTC', 0], ['ADA', 0], ['DOT', 0]] #This list will contain every crypto we use and its price
potential_harvest_dates = []
user_buys = []

basket = [['BTC', 1]]
basket_1 = [['BTC', 0.4], ['ETH', 0.3], ['LTC', 0.2], ['ADA', 0.1]]
basket_2 = [['BTC', 0.3], ['ETH', 0.4], ['LTC', 0.2], ['DOT', 0.1]]
basket_3 = [['BTC', 0.5], ['ETH', 0.2], ['LTC', 0.15], ['DOT', 0.15]]
basket_4 = [['BTC', 0.3], ['ETH', 0.4], ['LTC', 0.15], ['ADA', 0.15]]
test_baskets = [basket_1, basket_2, basket_3, basket_4]
all_baskets = [basket]

user_btc_buys = [['BTC', '2022-03-16', '0.0002442', '41359.54'],
                 ['BTC', '2022-02-16', '0.0003442', '40359.54'],
                 ['BTC', '2022-01-16', '0.0002442', '39359.54'],
                 ['BTC', '2021-12-16', '0.0001442', '35359.54'],
                 ['BTC', '2021-11-16', '0.0002442', '32359.54'],
                 ['BTC', '2021-10-16', '0.0004442', '42359.54'],
                 ['BTC', '2021-09-16', '0.0002442', '48359.54'],
                 ['BTC', '2021-08-16', '0.0003442', '49359.54'],
                 ['BTC', '2021-07-16', '0.0002442', '50359.54'],
                 ['BTC', '2021-06-16', '0.0003442', '48359.54']]

user_eth_buys = [['ETH', '2022-03-16', '0.002442', '3000'],
                 ['ETH', '2022-02-16', '0.003442', '2950.54'],
                 ['ETH', '2022-01-16', '0.002442', '2950.54'],
                 ['ETH', '2021-12-16', '0.001442', '2800.54'],
                 ['ETH', '2021-11-16', '0.002442', '2650.54'],
                 ['ETH', '2021-10-16', '0.004442', '3050.54'],
                 ['ETH', '2021-09-16', '0.002442', '3200.54'],
                 ['ETH', '2021-08-16', '0.003442', '3300.54'],
                 ['ETH', '2021-07-16', '0.002442', '3400.54'],
                 ['ETH', '2021-06-16', '0.003442', '3300.54']]

user_ltc_buys = [['LTC', '2022-03-16', '0.0078125', '128'],
                 ['LTC', '2022-02-16', '0.0078125', '124'],
                 ['LTC', '2022-01-16', '0.0078125', '126'],
                 ['LTC', '2021-12-16', '0.0078125', '118'],
                 ['LTC', '2021-11-16', '0.0078125', '100'],
                 ['LTC', '2021-10-16', '0.0078125', '128'],
                 ['LTC', '2021-09-16', '0.0078125', '135'],
                 ['LTC', '2021-08-16', '0.0078125', '138'],
                 ['LTC', '2021-07-16', '0.0078125', '140'],
                 ['LTC', '2021-06-16', '0.0078125', '150']]

user_ADA_buys = [['ADA', '2022-03-16', '1', '1'],
                 ['ADA', '2022-02-16', '1', '0.95'],
                 ['ADA', '2022-01-16', '1', '0.98'],
                 ['ADA', '2021-12-16', '1', '0.92'],
                 ['ADA', '2021-11-16', '1', '0.87'],
                 ['ADA', '2021-10-16', '1', '0.98'],
                 ['ADA', '2021-09-16', '1', '1.01'],
                 ['ADA', '2021-08-16', '1', '1.07'],
                 ['ADA', '2021-07-16', '1', '1.08'],
                 ['ADA', '2021-06-16', '1', '1.12']]

user_dot_buys = [['DOT', '2022-03-16', '0.06818', '22'],
                 ['DOT', '2022-02-16', '0.06818', '21'],
                 ['DOT', '2022-01-16', '0.06818', '22'],
                 ['DOT', '2021-12-16', '0.06818', '20'],
                 ['DOT', '2021-11-16', '0.06818', '18'],
                 ['DOT', '2021-10-16', '0.06818', '21'],
                 ['DOT', '2021-09-16', '0.06818', '23'],
                 ['DOT', '2021-08-16', '0.06818', '25'],
                 ['DOT', '2021-07-16', '0.06818', '26'],
                 ['DOT', '2021-06-16', '0.06818', '26']]

def predict_loss(all_crypto_prices, user): # This is the function that we would run periodically to determine if we will send a notification to our users
    """Checks potential for tax-loss harvesting."""
    today = date.today()
    threshold = -0.1

    #get dates where there is potential to harvest
    for crypto_price in all_crypto_prices: #loop through every currency
        for i in range(365): #loop through the previous year
            loop_day = today - timedelta(days = i)
            spot_price = get_spot_price(crypto_price[0]+'-USD', loop_day, user)
            amount = float(spot_price["amount"])
            change_in_price = float(crypto_price[1]) - (amount) 
            if ((change_in_price/amount) <= threshold):
                potential_harvest_dates.append([crypto_price[0], loop_day])

    print ("............................................")
    print ("These are the days with potential to harvest:")
    print (potential_harvest_dates)



def harvest(user, all_crypto_prices):
    
    #all_baskets = get_baskets()
    basket = combine_baskets(all_baskets)

    for coin in basket:
        for price in all_crypto_prices:
            if coin[0] == price[0]:
                coin.append(price[1])

    for coin in basket:
        user_buys = get_user_buys(user)
        total_amount_of_coin = float(user.client.get_account(coin[0])['balance']['amount'])
        amount_to_sell, net_losses = get_amount(user_buys, coin[2], coin[0], total_amount_of_coin)
        coin.append(total_amount_of_coin)
        coin.append(amount_to_sell)
        coin.append(net_losses)

    """(total_btc_to_sell, btc_net_losses) = get_amount(user_btc_buys, 45000, 'BTC', 0.002842)
    basket[0].append(0.002842)
    basket[0].append(total_btc_to_sell)
    basket[0].append(btc_net_losses)
    (total_eth_to_sell, eth_net_losses) = get_amount(user_eth_buys, 3000, 'ETH', 0.02842)
    basket[1].append(0.02842)
    basket[1].append(total_eth_to_sell)
    basket[1].append(eth_net_losses)
    (total_ltc_to_sell, ltc_net_losses) = get_amount(user_ltc_buys, 150, 'LTC', 0.078125)
    basket[2].append(0.078125)
    basket[2].append(total_ltc_to_sell)
    basket[2].append(ltc_net_losses)
    (total_ADA_to_sell, ADA_net_losses) = get_amount(user_ADA_buys, 1.2, 'ADA', 10)
    basket[3].append(10)
    basket[3].append(total_ADA_to_sell)
    basket[3].append(ADA_net_losses)
    (total_dot_to_sell, dot_net_losses) = get_amount(user_dot_buys, 22, 'DOT', 0.6818)
    basket[4].append(0.6818)
    basket[4].append(total_dot_to_sell)
    basket[4].append(dot_net_losses)"""

    trades = get_trades(basket)
    return trades

    #will pull baskets from the database
def get_baskets():
    baskets = [basket]
    return baskets;

def combine_baskets(all_baskets):

    combined_basket = []
    total_basket_count = len(all_baskets)
    add_coin = True

    for basket in all_baskets:
        for coin in basket:
            for pre_existing_coin in combined_basket:
                if coin[0] == pre_existing_coin[0]:
                    add_coin = False
                    #COMBINE THE COINS AND PERCENTAGES INTO THE NEW BASKET
                    pre_existing_coin[1] = (pre_existing_coin[1]) + (coin[1]/total_basket_count)
                    break
                else:
                    add_coin = True
            if add_coin == True:
                combined_basket.append(coin)
                index = len(combined_basket) - 1
                combined_basket[index][1] = coin[1]/total_basket_count

    print(combined_basket)
    return combined_basket

def get_user_buys(user):

    all_buys = user.client.get_buys(user.client.get_account('BTC')['id'])

    for buy in all_buys["data"]:

        date = buy["created_at"]
        date = re.sub(r'T.*', '', date)
        amount = str(buy["amount"])
        amount = amount.split(' ')[-1]
        unit_price = buy["unit_price"]["amount"]
        user_buys.append(['BTC', date, amount, unit_price])

    return user_buys


def get_amount(user_buys, current_price_of_coin, crypto, total_amount_of_coin):

    threshold = 0.1
    #total_amount_of_coin = 0.002842 #TEST DATA
    total_worth = current_price_of_coin * total_amount_of_coin
    total_amount_in_buys = 0
    shortened_buys = []

    #THIS GOES THROUGH AND ELIMINATES ALL IRRELEVANT BUYS (buys that are too old)
    for buy in user_buys:
        total_amount_in_buys = total_amount_in_buys + float(buy[2])
        print (total_amount_in_buys)
        if total_amount_in_buys > total_amount_of_coin:
            break
        else:
            shortened_buys.append(buy)
    user_buys = shortened_buys

    #THIS SORTS THE BUYS FROM OLDEST TO NEWEST
    user_buys = sorted(user_buys, key=lambda x: datetime.datetime.strptime(x[1], "%Y-%m-%d"))


    #THIS PART FIGURES OUT WHICH BUY TO SELL TO OPTIMIZE REALIZED LOSSES
    i=-1 #initialize iteration for the loop at -1 so that each iteration corresponds with list number
    net_investment = 0
    net_gains = 0
    maximum_loss = 0
    optimal_buy_to_harvest = 0
    for buy in user_buys:
        i=i+1;
        change_in_price = (current_price_of_coin - float(buy[3]))
        investment = (float(buy[2]) * float(buy[3]))
        net_investment = net_investment + investment
        gains = (current_price_of_coin * float(buy[2])) - (float(buy[3]) * float(buy[2]))
        net_gains = net_gains + gains
        buy.append(net_gains)
        if net_gains != 0:
            if (net_investment/net_gains) <= threshold:
                buy.append(True)
            else:
                buy.append(False)
        else:
            buy.append(False)
        if (net_gains < maximum_loss):
            maximum_loss = net_gains
            optimal_buy_to_harvest = i

    #user_buys =[crypto_id, yyyy-mm-dd, crypto_amount, unit_price, net_gains, above_threshold]

    #THIS DETERMINES THE TOTAL AMOUNT OF COIN TO SELL
    total_to_sell = 0
    for buy in user_buys:
        total_to_sell = total_to_sell + float(buy[2])
        if float(buy[4]) <= maximum_loss:
            break

    #IF THE OPTIMAL_BUY_TO_HARVEST RETURNS FALSE, THEN SET TOTAL TO SELL to 0
    if user_buys[optimal_buy_to_harvest][5] == False:
        total_to_sell = 0

    for buy in user_buys:
        print(buy)


    return (total_to_sell, maximum_loss)

    #user_buys = sorted(user_buys,key=lambda x:datetime.datetime.strptime(x[1],"%Y-%m-%d"))
    #print (user_buys)

def get_trades(basket): #basket = ['id', 'percentage', 'price of currency', 'amount of currency in account', 'sell amount', 'realized losses from selling that amount']

    #WE CAN ONLY SELL HALF OF THE DIFFERENT COINS AT ONE TIME.
    number_of_coins_in_basket = 0
    for coin in basket:
        number_of_coins_in_basket += 1

    max_coins_to_sell = number_of_coins_in_basket/2

    #CHECK CURRENT PERCENTAGES.
    account_balance = 0
    for coin in basket:
        account_balance += coin[2]*coin[3]

    print ("account balance")
    print (account_balance)

    for coin in basket:
        real_percentage = (coin[2]*coin[3])/account_balance
        if coin[1] > real_percentage:
            coin.append('buy')
        elif coin[1] < real_percentage:
            coin.append('sell')
        else:
            coin.append('stand')
        print ("real percentage")
        print (real_percentage)
        coin.append(coin[1]-real_percentage)
        # basket = ['id', 'percentage', 'price of currency', 'amount of currency in account', 'sell amount', 'realized losses from selling that amount'
        #           'buy/sell/stand', difference in percentage]

    print("basket:")
    print(basket)
    print(max_coins_to_sell)

    #CHOOSE SELLERS

    basket_minus_sellers = basket
    basket_of_sellers = []

    for i in range(int(max_coins_to_sell)):
        max_harvest = 0
        found_a_coin = False
        coin_to_sell = -1
        for coin in basket_minus_sellers:
            if (coin[5] <= max_harvest) & (coin[5] < 0) & (coin[6] == 'sell'):
                max_harvest = coin[5]
                coin_to_sell = basket_minus_sellers.index(coin)
                found_a_coin = True

        if not found_a_coin:
            for coin in basket_minus_sellers:
                if (coin[5] <= max_harvest) & (coin[5] < 0) & (coin[6] == 'stand'):
                    max_harvest = coin[5]
                    coin_to_sell = basket_minus_sellers.index(coin)

        basket_of_sellers.append([basket_minus_sellers[coin_to_sell][0], basket_minus_sellers[coin_to_sell][4]])
        del basket_minus_sellers[coin_to_sell]



    #SORT REMAINING COINS BY HOW UNDERWEIGHT THEY ARE
    basket_minus_sellers.sort(key=lambda row: (row[7]))

    i = -1;
    for coin in basket_of_sellers:
        i = i+1;
        coin.append(basket_minus_sellers[i][0])

    print("")
    print("basket of sellers:")
    print(basket_of_sellers)
    print("basket minus sellers:")
    print(basket_minus_sellers)

    return basket_of_sellers #['id to sell', 'amount to sell', 'what to buy']

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
    print(data)
    price = data["data"]["amount"] #price of the crypto
    return float(price)

def get_spot_price(currency_pair, date, user): #currency_pair must be in format like 'BTC-USD' and date must be in format like '2022-3-2'
    spot_price = user.client.get_spot_price(currency_pair=currency_pair, date=date)
    return spot_price
        

def process_investments(user):
    investing = True
    all_crypto_prices = get_all_crypto_prices()
    #spot_price = get_spot_price('BTC-USD', '2022-3-2', user)
    #print (f"the spot price is {spot_price}")
    #print (all_crypto_prices)
    trades = harvest(user, all_crypto_prices)
    #time.sleep(30)
    #predict_loss(all_crypto_prices, user), ['ADA', 0], ['DOT', 0]
    return trades

def use_test_data(user):
    investing = True
    all_crypto_prices = get_all_crypto_prices()

    #all_baskets = get_baskets()
    basket = combine_baskets(test_baskets)

    for coin in basket:
        for price in all_crypto_prices:
            if coin[0] == price[0]:
                coin.append(price[1])

    (total_btc_to_sell, btc_net_losses) = get_amount(user_btc_buys, 45000, 'BTC', 0.002842)
    basket[0].append(0.002842)
    basket[0].append(total_btc_to_sell)
    basket[0].append(btc_net_losses)
    (total_eth_to_sell, eth_net_losses) = get_amount(user_eth_buys, 3000, 'ETH', 0.02842)
    basket[1].append(0.02842)
    basket[1].append(total_eth_to_sell)
    basket[1].append(eth_net_losses)
    (total_ltc_to_sell, ltc_net_losses) = get_amount(user_ltc_buys, 150, 'LTC', 0.078125)
    basket[2].append(0.078125)
    basket[2].append(total_ltc_to_sell)
    basket[2].append(ltc_net_losses)
    (total_ADA_to_sell, ADA_net_losses) = get_amount(user_ADA_buys, 1.2, 'ADA', 10)
    basket[3].append(10)
    basket[3].append(total_ADA_to_sell)
    basket[3].append(ADA_net_losses)
    (total_dot_to_sell, dot_net_losses) = get_amount(user_dot_buys, 22, 'DOT', 0.6818)
    basket[4].append(0.6818)
    basket[4].append(total_dot_to_sell)
    basket[4].append(dot_net_losses)

    trades = get_trades(basket)

    return trades