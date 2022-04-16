"""
Scripts for transactions (deposit, buy, sell, withdraw).
"""
from flask import flash
from crypto_platform.dashboard.User import User
import time

# For the Database
from crypto_platform.models import BasketModel, BasketCryptoPercentageModel, UserBasketModel, UserBasketCryptoAmountModel, FailedBuyModel, FailedSellModel
from crypto_platform import db

"""Transaction Functions"""
def deposit(user, amount):
    """Deposits funds for the user."""
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
    basket = get_basket_from_database(basket_name)

    if user.get_cash_wallet_balance() < invest_amount:
        flash('Oh no! You do not have enough funds to invest. Please deposit more funds before buying.', 'error')
    elif get_failed_buys_from_database(user, basket):
        flash('Please retry your previous buys for ' + basket_name + ' before buying more.', 'error')
    else:
        
        crypto_percentages = get_crypto_percentages_from_database(basket)

        num_buys = 0
        num_failed_buys = 0
        last_error = ''

        for crypto_percentage in crypto_percentages:
            crypto = crypto_percentage.crypto # The cryptocurrency.
            percent = crypto_percentage.percentage # The percentage this cryptocurrency makes up in the basket.
            buy_amount = invest_amount * percent # The amount of this cryptocurrency to buy.

            num_buys += 1

            try:
                spot_price = float(user.client.get_spot_price(currency_pair = crypto + '-' + user.native_currency).amount)
                buy_amount_in_crypto = buy_amount / spot_price

                user.buy(crypto, buy_amount_in_crypto)

            except Exception as e:
                num_failed_buys += 1
                last_error = str(e)

                add_failed_buy_to_database(user, basket, crypto, buy_amount)

            else:
                amount = buy_amount_in_crypto
                user_basket_crypto_amount = get_user_basket_crypto_amount_from_database(user, basket, crypto)

                if user_basket_crypto_amount:
                    update_user_basket_crypto_amount_in_database(user_basket_crypto_amount, amount)
                else:
                    add_user_basket_crypto_amount_to_database(user, basket, crypto, amount)

        if num_failed_buys > 0:
            flash('Oh no! {} of your {} buys did not process, please retry in an hour. Error Code: {}'.format(num_failed_buys, num_buys, last_error), 'error')
        else:

            user_basket = get_user_basket_from_database(user, basket) # Get the user basket if it exists.

            if not user_basket: # If the user basket does not exists ...
                add_user_basket_to_database(user, basket) # add it.

            flash('Your buys processed successfully! You should receive several emails from Coinbase.', 'success')

def retry_buy_basket(user, basket_name):
    """
    Retries buying all of the user's failed buys.

    user: the user, represented as an object of the User class
    basket_name: the name of the user's selected basket
    """
    basket = get_basket_from_database(basket_name)
    failed_buys = get_failed_buys_from_database(user, basket)
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
                spot_price = float(user.client.get_spot_price(currency_pair = crypto + '-' + user.native_currency).amount)
                buy_amount_in_crypto = buy_amount / spot_price

                user.buy(crypto, buy_amount_in_crypto)

            except Exception as e:
                num_failed_buys += 1
                last_error = str(e)

            else:
                remove_failed_buy_from_database(failed_buy)

                amount = buy_amount_in_crypto
                user_basket_crypto_amount = get_user_basket_crypto_amount_from_database(user, basket, crypto)

                if user_basket_crypto_amount:
                    update_user_basket_crypto_amount_in_database(user_basket_crypto_amount, amount)
                else:
                    add_user_basket_crypto_amount_to_database(user, basket, crypto, amount)

        if num_failed_buys > 0:
            flash('Oh no! {} of your {} buys did not process, please retry in an hour. Error Code: {}'.format(num_failed_buys, num_buys, last_error), 'error')
        else:
            user_basket = get_user_basket_from_database(user, basket) # Get the user basket if it exists.

            if not user_basket: # If the user basket does not exists ...
                add_user_basket_to_database(user, basket) # add it.

            flash('Your buys processed successfully! You should receive several emails from Coinbase.', 'success')

def sell_basket(user, basket_name):
    """
    Sells a basket for the user.

    user: the user, represented as an object of the User class
    basket_name: the name of the user's selected basket
    """
    basket = get_basket_from_database(basket_name)

    if get_failed_sells_from_database(user, basket):
        flash('Please retry your previous sells for ' + basket_name + ' before selling more.', 'error')
    else:

        user_basket_crypto_amounts = get_user_basket_crypto_amounts_from_database(user, basket)

        num_sells = 0
        num_failed_sells = 0
        last_error = ''

        for user_basket_crypto_amount in user_basket_crypto_amounts:
            crypto = user_basket_crypto_amount.crypto # The cryptocurrency.
            sell_amount = user_basket_crypto_amount.amount # The amount of this cryptocurrency to sell.

            num_sells += 1
        
            try:
                user.sell(crypto, sell_amount)

            except Exception as e:
                num_failed_sells += 1
                last_error = str(e)

                add_failed_sell_to_database(user, basket, crypto, sell_amount)

            else:
                remove_user_basket_crypto_amount_from_database(user_basket_crypto_amount)

        if num_failed_sells > 0:
            flash('Oh no! {} of your {} sells did not process, please retry in an hour. Error Code: {}'.format(num_failed_sells, num_sells, last_error), 'error')     
        else:
            user_basket = get_user_basket_from_database(user, basket)
            remove_user_basket_from_database(user_basket)
            flash('Your sells processed successfully! You should receive several emails from Coinbase.', 'success')

def retry_sell_basket(user, basket_name):
    """
    Retries selling all the user's failed sells.

    user: the user, represented as an object of the User class
    basket_name: the name of the user's selected basket
    """
    basket = get_basket_from_database(basket_name)
    failed_sells = get_failed_sells_from_database(user, basket)

    num_sells = 0
    num_failed_sells = 0
    last_error = ''

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
            remove_failed_sell_from_database(failed_sell)

            user_basket_crypto_amount = get_user_basket_crypto_amount_from_database(user, basket, crypto)
            remove_user_basket_crypto_amount_from_database(user_basket_crypto_amount)

    if num_failed_sells > 0:
        flash('Oh no! {} of your {} sells did not process, please retry in an hour. Error Code: {}'.format(num_failed_sells, num_sells, last_error), 'error')     
    else:
        user_basket = get_user_basket_from_database(user, basket)
        remove_user_basket_from_database(user_basket)
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

# Database Functions
def get_basket_from_database(basket_name):
    basket = BasketModel.query.filter_by(name = basket_name).first()
    return basket

def get_crypto_percentages_from_database(basket):
    crypto_percentages = BasketCryptoPercentageModel.query.filter_by(basket_id = basket.id).all()
    return crypto_percentages

def add_user_basket_to_database(user, basket):
    new_user_basket = UserBasketModel(user_id = user.coinbase_id,
                                      basket_id = basket.id)
    db.session.add(new_user_basket)
    db.session.commit()

def get_user_basket_from_database(user, basket):
    user_basket = UserBasketModel.query.filter_by(user_id = user.coinbase_id, basket_id = basket.id).first()
    return user_basket

def remove_user_basket_from_database(user_basket):
    db.session.delete(user_basket)
    db.session.commit()

def add_user_basket_crypto_amount_to_database(user, basket, crypto, amount):
    user_basket_crypto_amount = UserBasketCryptoAmountModel(user_id = user.coinbase_id,
                                                            basket_id = basket.id,
                                                            crypto = crypto,
                                                            amount = amount)
    db.session.add(user_basket_crypto_amount)
    db.session.commit()

def get_user_basket_crypto_amounts_from_database(user, basket):
    user_basket_crypto_amount = UserBasketCryptoAmountModel.query.filter_by(user_id = user.coinbase_id, basket_id = basket.id).all()
    return user_basket_crypto_amount

def get_user_basket_crypto_amount_from_database(user, basket, crypto):
    user_basket_crypto_amount = UserBasketCryptoAmountModel.query.filter_by(user_id = user.coinbase_id, basket_id = basket.id, crypto = crypto).first()
    return user_basket_crypto_amount

def update_user_basket_crypto_amount_in_database(user_basket_crypto_amount, amount):
    user_basket_crypto_amount.amount += amount

    db.session.add(user_basket_crypto_amount)
    db.session.commit()

def remove_user_basket_crypto_amount_from_database(user_basket_crypto_amount):
    db.session.delete(user_basket_crypto_amount)
    db.session.commit()

def add_failed_buy_to_database(user, basket, crypto, buy_amount):
    failed_buy = FailedBuyModel(user_id = user.coinbase_id,
                                basket_id = basket.id,
                                crypto = crypto,
                                buy_amount = buy_amount)
    db.session.add(failed_buy)
    db.session.commit()

def get_failed_buys_from_database(user, basket):
    failed_buys = FailedBuyModel.query.filter_by(user_id = user.coinbase_id, basket_id = basket.id).all()
    return failed_buys

def remove_failed_buy_from_database(failed_buy):
    db.session.delete(failed_buy)
    db.session.commit()

def add_failed_sell_to_database(user, basket, crypto, sell_amount):
    failed_sell = FailedSellModel(user_id = user.coinbase_id,
                                  basket_id = basket.id,
                                  crypto = crypto,
                                  sell_amount = sell_amount)
    db.session.add(failed_sell)
    db.session.commit()

def get_failed_sells_from_database(user, basket):
    failed_sells = FailedSellModel.query.filter_by(user_id = user.coinbase_id, basket_id = basket.id).all()
    return failed_sells

def remove_failed_sell_from_database(failed_sell):
    db.session.delete(failed_sell)
    db.session.commit()

    