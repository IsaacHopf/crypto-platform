"""
Scripts for transactions (deposit, buy, sell, withdraw).
"""

from flask import flash
from crypto_platform.dashboard.User import User
import time, re

# For the Database
from crypto_platform.models import BasketModel, BasketCryptoPercentageModel, UserBasketModel, UserBasketCryptoAmountModel, FailedBuyModel, FailedSellModel
from crypto_platform import db

"""Transaction Functions"""
def deposit(user, amount):
    """Deposits funds for the user."""
    if hasattr(user, 'bank_payment_method_id'):
        try:
            user.deposit(amount)
        except Exception as e:
            flash('Oh no! Your deposit did not process, please try again in an hour. Error Code: ' + str(e), 'error')
        else:
            flash('Your deposit processed successfully! You should receive an email from Coinbase.', 'success')

def buy_basket(user, basket_name, invest_amount):
    """
    Buys a basket for the user.

    user: the user, represented as an object of the User class
    basket_name: the name of the user's selected basket
    invest_amount: the amount to invest for the selected basket (in the user's native currency)
    """
    basket = BasketModel.get_by_name(basket_name)

    if user.get_cash_wallet_balance() < invest_amount:
        flash('Oh no! You do not have enough funds to buy. Please deposit more funds before buying.', 'error')
    elif get_failed_buys_from_database(user, basket):
        flash('Please retry your previous buys for ' + basket_name + ' before buying more.', 'error')
    else:
        
        crypto_percentages = BasketCryptoPercentageModel.get_all_by_basket(basket)

        num_buys = 0
        num_failed_buys = 0
        last_error = ''

        for crypto_percentage in crypto_percentages:
            crypto = crypto_percentage.crypto # The cryptocurrency.
            percent = crypto_percentage.percentage # The percentage this cryptocurrency makes up in the basket.
            buy_amount = invest_amount * percent # The amount of this cryptocurrency to buy.

            num_buys += 1

            try:
                buy = user.buy(crypto, buy_amount)

            except Exception as e:
                num_failed_buys += 1
                last_error = str(e)

                FailedBuyModel.add(user, basket, crypto, buy_amount)

            else:
                bought_amount = buy['amount']['amount']
                user_basket_crypto_amount = UserBasketCryptoAmountModel.get_by_user_and_basket_and_crypto(user, basket, crypto)

                if user_basket_crypto_amount:
                    UserBasketCryptoAmountModel.update(user_basket_crypto_amount, bought_amount)
                else:
                    UserBasketCryptoAmountModel.add(user, basket, crypto, bought_amount)

        if num_failed_buys > 0:
            flash('Oh no! {} of your {} buys did not process, please retry in an hour. Error Code: {}'.format(num_failed_buys, num_buys, last_error), 'error')
        else:
            user_basket = UserBasketModel.get_by_user_and_basket(user, basket) # Get the user basket if it exists.

            if not user_basket: # If the user basket does not exists ...
                UserBasketModel.add(user, basket) # add it.

            flash('Your buys processed successfully! You should receive several emails from Coinbase.', 'success')

def retry_buy_basket(user, basket_name):
    """
    Retries buying all of the user's failed buys.

    user: the user, represented as an object of the User class
    basket_name: the name of the user's selected basket
    """
    basket = BasketModel.get_by_name(basket_name)
    failed_buys = FailedBuyModel.get_all_by_user_and_basket(user, basket)
    total_buy_amount = 0

    for failed_buy in failed_buys:
        total_buy_amount += failed_buy.buy_amount

    if user.get_cash_wallet_balance() < total_buy_amount:
        flash('Oh no! You do not have enough funds to invest. Please deposit more funds before retrying.', 'error')
    else:

        num_buys = 0
        num_failed_buys = 0
        last_error = ''
        
        for failed_buy in failed_buys:
            crypto = failed_buy.crypto
            buy_amount = failed_buy.buy_amount

            num_buys += 1

            try:
                buy = user.buy(crypto, buy_amount)

            except Exception as e:
                num_failed_buys += 1
                last_error = str(e)

            else:
                FailedBuyModel.remove(failed_buy)

                bought_amount = buy['amount']['amount']
                user_basket_crypto_amount = UserBasketCryptoAmountModel.get_by_user_and_basket_and_crypto(user, basket, crypto)

                if user_basket_crypto_amount:
                    UserBasketCryptoAmountModel.update(user_basket_crypto_amount, bought_amount)
                else:
                    UserBasketCryptoAmountModel.add(user, basket, crypto, bought_amount)

        if num_failed_buys > 0:
            flash('Oh no! {} of your {} buys did not process, please retry in an hour. Error Code: {}'.format(num_failed_buys, num_buys, last_error), 'error')
        else:
            user_basket = UserBasketModel.get_by_user_and_basket(user, basket) # Get the user basket if it exists.

            if not user_basket: # If the user basket does not exists ...
                UserBasketModel.add(user, basket) # add it.

            flash('Your buys processed successfully! You should receive several emails from Coinbase.', 'success')

def sell_basket(user, basket_name):
    """
    Sells a basket for the user.

    user: the user, represented as an object of the User class
    basket_name: the name of the user's selected basket
    """
    basket = BasketModel.get_by_name(basket_name)

    if get_failed_sells_from_database(user, basket):
        flash('Please retry your previous sells for ' + basket_name + ' before selling more.', 'error')
    else:

        user_basket_crypto_amounts = UserBasketCryptoAmountModel.get_all_by_user_and_basket(user, basket)

        num_sells = 0
        num_failed_sells = 0
        last_error = ''

        for user_basket_crypto_amount in user_basket_crypto_amounts:
            crypto = user_basket_crypto_amount.crypto # The cryptocurrency.
            bought_amount = user_basket_crypto_amount.amount # The amount of this cryptocurrency originally bought.
            user_crypto_amounts = UserBasketCryptoAmountModel.get_all_by_user_and_crypto(user, crypto)
            total_bought_amount = 0

            for user_crypto_amount in user_crypto_amounts: # For all of the user's user_basket_crypto_amounts with the same cryptocurrency ...
                total_bought_amount += user_crypto_amount.amount # add their originally bought amounts to the total amount.

            current_balance = user.get_crypto_wallet_balance_in_cryptocurrency(crypto) # Get the current balance of the specified cryptocurrency wallet.
            sell_amount = (bought_amount / total_bought_amount) * current_balance # Calculate the amount to sell.

            num_sells += 1
        
            try:
                user.sell(crypto, sell_amount)

            except Exception as e:
                num_failed_sells += 1
                last_error = str(e)

                FailedSellModel.add(user, basket, user_basket_crypto_amount)

            else:
                UserBasketCryptoAmountModel.remove(user_basket_crypto_amount)

        if num_failed_sells > 0:
            flash('Oh no! {} of your {} sells did not process, please retry in an hour. Error Code: {}'.format(num_failed_sells, num_sells, last_error), 'error')     
        else:
            user_basket = UserBasketModel.get_by_user_and_basket(user, basket)
            UserBasketModel.remove(user_basket)
            flash('Your sells processed successfully! You should receive several emails from Coinbase.', 'success')

def retry_sell_basket(user, basket_name):
    """
    Retries selling all the user's failed sells.

    user: the user, represented as an object of the User class
    basket_name: the name of the user's selected basket
    """
    basket = BasketModel.get(basket_name)
    failed_sells = FailedSellModel.get_all_by_user_and_basket(user, basket)

    num_sells = 0
    num_failed_sells = 0
    last_error = ''

    for failed_sell in failed_sells:
        user_basket_crypto_amount = UserBasketCryptoAmountModel.get_by_id(failed_sell.user_basket_crypto_amount_id)

        crypto = user_basket_crypto_amount.crypto # The cryptocurrency.
        bought_amount = user_basket_crypto_amount.amount # The amount of this cryptocurrency originally bought.
        user_crypto_amounts = UserBasketCryptoAmountModel.get_all_by_user_and_crypto(user, crypto)
        total_bought_amount = 0

        for user_crypto_amount in user_crypto_amounts: # For all of the user's user_basket_crypto_amounts with the same cryptocurrency ...
            total_bought_amount += user_crypto_amount.amount # add their originally bought amounts to the total amount.

        current_balance = user.get_crypto_wallet_balance_in_cryptocurrency(crypto) # Get the current balance of the specified cryptocurrency wallet.
        sell_amount = (bought_amount / total_bought_amount) * current_balance # Calculate the amount to sell.

        num_sells += 1

        try:
            user.sell(crypto, sell_amount)

        except Exception as e:
            num_failed_sells += 1
            last_error = str(e)

        else:
            FailedSellModel.remove(failed_sell)
            UserBasketCryptoAmountModel.remove(user_basket_crypto_amount)

    if num_failed_sells > 0:
        flash('Oh no! {} of your {} sells did not process, please retry in an hour. Error Code: {}'.format(num_failed_sells, num_sells, last_error), 'error')     
    else:
        user_basket = UserBasketModel.get_by_user_and_basket(user, basket)
        UserBasketModel.remove(user_basket)
        flash('Your sells processed successfully! You should receive several emails from Coinbase.', 'success')

def withdraw(user, amount):
    """Withdraws funds for the user."""
    if user.get_cash_wallet_balance() < amount:
        flash('Oh no! You cannot withdraw that much. Please withdraw less funds or sell a basket.', 'error')
    else:
        try:
            user.withdraw(amount)
        except Exception as e:
            if re.search("withdrawal_limit_exceeded", str(e)):
                flash('Oh no! Your withdraw did not process. This may be because your buys and sells have not completely processed, which can take 5 - 7 business days. Error Code: ' + str(e), 'error')
            else:
                flash('Oh no! Your withdraw did not process, please try again in an hour. Error Code: ' + str(e), 'error')
        else:
            flash('Your withdraw processed successfully! You should receive an email from Coinbase.', 'success')


    