# For Coinbase
from coinbase.wallet.client import OAuthClient
import re

# For Exception Handling
from coinbase.wallet.error import RateLimitExceededError, UnverifiedEmailError
from flask import flash, session
from  datetime import datetime, timedelta
import threading
from crypto_platform import connect
from crypto_platform.dashboard import notify 

# For the Database
from crypto_platform.models import UserModel
from crypto_platform import db

class User(object):
    """Represents the user of our platform."""

    def __init__(self, tokens):
        try:
            self.client = OAuthClient(tokens['access_token'], tokens['refresh_token']) # The client used to connect to the user's Coinbase account.
        except RateLimitExceededError as e:
            flash('Oops, an error occurred, please try logging in again in a minute. Error Code: ' + str(e), 'error')
        except UnverifiedEmailError:
            flash('Please verify your Coinbase email before proceeding.', 'error')
        except Exception as e:
            flash('Oops, an error occurred. Error Code: ' + str(e), 'error')

        self.current_user = self.client.get_current_user()
        self.coinbase_id = str(self.current_user['id'])
        self.email = self.current_user['email']
        self.native_currency = self.current_user['native_currency']

        if UserModel.query.get(self.coinbase_id) is None: # If the user does not exist in the database ...
            self.__add_user_to_database() # add them.

        self.payment_methods = self.client.get_payment_methods()
        self.cash_payment_method_id = self.__get_cash_payment_method_id() # The id of the user's Cash payment method (which links to their Cash wallet).
        try:
            self.bank_payment_method_id = self.__get_bank_payment_method_id() # The id of the bank payment method the user added.
        except:
            flash('Please add your bank account as a payment method on Coinbase before proceeding.', 'error')

    def __add_user_to_database(self):
        """Adds the current user to the database."""
        new_user = UserModel(
            id = self.coinbase_id,
            email = self.email)

        db.session.add(new_user)
        db.session.commit()

    def __get_cash_payment_method_id(self):
        """Gets the user's Cash payment method. This payment method always exists and links directly to the user's Cash wallet (which is in their native currency)."""
        for payment_method in self.payment_methods['data']:
            if re.match("Cash", payment_method['name']) is not None: # The name of the Cash payment method always starts with "Cash".
                return payment_method['id']

    def __get_bank_payment_method_id(self):
        """Gets the bank payment method the user added. If they have not added a bank payment method, asks them to add one."""
        for payment_method in self.payment_methods['data']:
            if re.search("bank_account", payment_method['type']) is not None and payment_method['allow_withdraw'] == True: # The type of a bank payment method always contains "bank_account"
                return payment_method['id']

        # If the user has not added their bank payment method
        raise Exception('User has not added bank payment method!')

    def buy_with_cash_payment_method(self, crypto, total):
        """
        Buys cryptocurrency for the user and pays with the user's cash wallet. This is used when tax loss harvesting.

        crypto: the cryptocurrency symbol (Ex. 'BTC' for Bitcoin)
        total: the total that will be spent (in the user's native currency)
        """
        retries = 0

        def transaction():
            if 'tokens' not in session: # If the user's tokens have expired ...
                connect.coinbase_login # redirect them to login.

            elif (datetime.now() - session['tokens_created_at'] > timedelta(hours=1.5)): # If the user's tokens are close to expiring
                self.client.refresh() # refresh them.
                session['tokens_created_at'] = datetime.now()
                transaction()

            else:
                try:
                    account_id = self.client.get_account(crypto)['id'] # Finds the wallet of the specified cryptocurrency.

                    self.client.buy(account_id, # Buys the specified cryptocurrency.
                            total = total, # Buys the specified total (a portion of this total is used for fees) ...
                            currency = self.native_currency, # in the user's native currency.
                            payment_method = self.cash_payment_method_id) # Pays with the user's cash wallet.

                except Exception as e: # If there was an exception ...
                    if retries < 29:
                        retries += 1
                        timer = threading.Timer(60.0, transaction) # try again in a minute.
                        timer.start()
                    else: # If tried 29 times ...
                        flash('Oops, your investment was not processed, please contact support. Error Code: ' + str(e), 'error') # flash the error ...
                        notify.send_transaction_error_notification(self.email, e) # and send an email notification.

        transaction()

    def buy_with_bank_payment_method(self, crypto, total):
        """
        Buys cryptocurrency for the user and pays with the user's bank payment method. This is used for initial investments.

        crypto: the cryptocurrency symbol (Ex. 'BTC' for Bitcoin)
        total: the total that will be spent (in the user's native currency)
        """
        retries = 0

        def transaction():
            if 'tokens' not in session: # If the user's tokens have expired ...
                connect.coinbase_login # redirect them to login.

            elif (datetime.now() - session['tokens_created_at'] > timedelta(hours=1.5)): # If the user's tokens are close to expiring
                self.client.refresh() # refresh them.
                session['tokens_created_at'] = datetime.now()
                transaction()

            else:
                try:
                    account_id = self.client.get_account(crypto)['id'] # Finds the wallet of the specified cryptocurrency.

                    self.client.buy(account_id, # Buys the specified cryptocurrency.
                                    total = total, # Buys the specified total (a portion of this total is used for fees) ...
                                    currency = self.native_currency, # in the user's native currency.
                                    payment_method = self.bank_payment_method_id) # Pays with the user's bank payment method.

                except Exception as e: # If there was an exception ...
                    if retries < 29:
                        retries += 1
                        timer = threading.Timer(60.0, transaction) # try again in a minute.
                        timer.start()
                    else: # If tried 29 times ...
                        flash('Oops, your investment was not processed, please contact support. Error Code: ' + str(e), 'error') # flash the error ...
                        notify.send_transaction_error_notification(self.email, e) # and send an email notification.

        transaction()    

    def test_buy(self, crypto, total):
        """
        Tests buying cryptocurrency for the user by not committing the buy order. Thus, the buy is never processed.

        crypto: the cryptocurrency symbol (Ex. 'BTC' for Bitcoin)
        total: the total that will be spent (in the user's native currency)
        return: the buy order (what it would look like had the buy been processed), as a dict
        """
        account_id = self.client.get_account(crypto)['id'] # Finds the account, or wallet, of the specified cryptocurrency

        return self.client.buy(account_id, # Buys the specified cryptocurrency.
                               total = total, # Buys the specified total (a portion of this total is used for fees) ...
                               currency = self.native_currency, # in the user's native currency.
                               commit = False, # Prevents the buy order from processing.
                               quote = True) # Generates the buy order (what it would look like had the buy been processed).

    def sell(self, crypto, amount):
        """
        Sells cryptocurrency for the user. Deposits the earnings into the user's Cash wallet.

        crypto: the cryptocurrency symbol (Ex. 'BTC' for Bitcoin)
        amount: the amount to sell (in the user's native currency)
        """
        retries = 0

        def transaction():
            if 'tokens' not in session: # If the user's tokens have expired ...
                connect.coinbase_login # redirect them to login.

            elif (datetime.now() - session['tokens_created_at'] > timedelta(hours=1.5)): # If the user's tokens are close to expiring
                self.client.refresh() # refresh them.
                session['tokens_created_at'] = datetime.now()
                transaction()

            else:
                try:
                    account_id = self.client.get_account(crypto)['id'] # Finds the wallet of the specified cryptocurrency.

                    self.client.sell(account_id, # Sells the specified cryptocurreny.
                                     amount = amount, # Sells the specified amount (a portion of this amount is used for fees) ...
                                     currency = self.native_currency, # in the user's native currency.
                                     payment_method = self.cash_payment_method_id) # Deposits the money into the user's Cash wallet.

                except Exception as e: # If there was an exception ...
                    if retries < 29:
                        retries += 1
                        timer = threading.Timer(60.0, transaction) # try again in a minute.
                        timer.start()
                    else: # If tried 29 times ...
                        flash('Oops, your investment was not processed, please contact support. Error Code: ' + str(e), 'error') # flash the error ...
                        notify.send_transaction_error_notification(self.email, e) # and send an email notification.

        transaction()

    def withdraw(self, amount):
        """
        Withdraws money from the user's Cash wallet and deposits the earnings into the user's bank payment method.

        amount: the amount to withdraw (in the user's native currency)
        """
        retries = 0

        def transaction():
            if 'tokens' not in session: # If the user's tokens have expired ...
                connect.coinbase_login # redirect them to login.

            elif (datetime.now() - session['tokens_created_at'] > timedelta(hours=1.5)): # If the user's tokens are close to expiring
                self.client.refresh() # refresh them.
                session['tokens_created_at'] = datetime.now()
                transaction()

            else:
                try:
                    account_id = self.client.get_account(self.native_currency)['id'] # Finds the user's Cash wallet.

                    self.client.withdraw(account_id, # Withdraws from the user's Cash wallet.
                                 amount = amount, # Withdraws the specified amount ...
                                 currency = self.native_currency, # in the user's native currency.
                                 payment_method = self.bank_payment_method_id) # Deposits the money into the user's bank payment method.

                except Exception as e: # If there was an exception ...
                    if retries < 29:
                        retries += 1
                        timer = threading.Timer(60.0, transaction) # try again in a minute.
                        timer.start()
                    else: # If tried 29 times ...
                        flash('Oops, your investment was not processed, please contact support. Error Code: ' + str(e), 'error') # flash the error ...
                        notify.send_transaction_error_notification(self.email, e) # and send an email notification.

        transaction()

    def get_cash_wallet_balance(self):
        """
        Gets the balance of the user's Cash wallet.

        return: the balance, as a float
        """
        balance = float(self.client.get_account(self.native_currency)['balance']['amount'])
        return balance

    def logout(self):
        """Logs out the user by deleting their tokens session variable and revoking their access token."""
        session.pop('tokens', None)
        self.client.revoke()
