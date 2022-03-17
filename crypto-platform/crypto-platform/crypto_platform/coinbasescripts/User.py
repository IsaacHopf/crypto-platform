from coinbase.wallet.client import OAuthClient
import re
import time

class User(object):
    """Represents the user of our platform."""

    def __init__(self, tokens):
        self.client = OAuthClient(tokens['access_token'], tokens['refresh_token']) # The client used to connect to the user's Coinbase account.

        self.current_user = self.client.get_current_user()
        self.native_currency = self.current_user['native_currency']
        self.email = self.current_user['email']

        self.payment_methods = self.client.get_payment_methods()
        self.cash_payment_method_id = self.__get_cash_payment_method_id() # The id of the user's Cash payment method (which links to their Cash wallet).
        self.bank_payment_method_id = self.__get_bank_payment_method_id() # The id of the bank payment method the user added.

        ######Test buy
        #print("BUY $2 of BTC")
        #self.buy('BTC', 2)
        #time.sleep(30)
        #print("BTC Wallet: ")
        #print(self.client.get_account('BTC'))
        #print("USD Wallet: ")
        #print(self.client.get_account('USD'))

    def __get_cash_payment_method_id(self):
        """Gets the user's Cash payment method. This payment method always exists and links directly to the user's Cash wallet (which is in their native currency)."""
        for payment_method in self.payment_methods['data']:
            if re.match("Cash", payment_method['name']) is not None: # The name of the Cash payment method always starts with "Cash".
                return payment_method['id']
            # There will always be a Cash account, so do I need any error handling here?

    def __get_bank_payment_method_id(self):
        """Gets the bank payment method the user added. If they have not added a bank payment method, asks them to add one."""
        for payment_method in self.payment_methods['data']:
            if re.search("bank_account", payment_method['type']) is not None and payment_method['allow_withdraw'] == True: # The type of a bank payment method always contains "bank_account"
                return payment_method['id']

        # If the user hasn't added a payment method
        print("Please add your Bank account as a payment method.")
        # Add code for UI or call function that handles this
        # Make sure that user.added_payment_method is defined after the user adds the payment method
        # Could ask them to log in again

    def buy_with_cash_payment_method(self, crypto, total):
        """
        Buys cryptocurrency for the user and pays with the user's cash wallet. This is used when tax loss harvesting.

        crypto: the cryptocurrency symbol (Ex. 'BTC' for Bitcoin)
        total: the total that will be spent (in the user's native currency)
        """
        account_id = self.client.get_account(crypto)['id'] # Finds the wallet of the specified cryptocurrency.

        try:
            self.client.buy(account_id, # Buys the specified cryptocurrency.
                            total = total, # Buys the specified total (a portion of this total is used for fees) ...
                            currency = self.native_currency, # in the user's native currency.
                            payment_method = self.cash_payment_method_id) # Pays with the user's cash wallet.
        except RateLimitExceededError:
            print("The buy was too large. Please check your Account Limits on Coinbase or make a smaller investment.")
        except:
            print("The buy did not process. Please try again.")

    def buy_with_bank_payment_method(self, crypto, total):
        """
        Buys cryptocurrency for the user and pays with the user's bank payment method. This is used for initial investments.

        crypto: the cryptocurrency symbol (Ex. 'BTC' for Bitcoin)
        total: the total that will be spent (in the user's native currency)
        """
        account_id = self.client.get_account(crypto)['id'] # Finds the wallet of the specified cryptocurrency.

        try:
            self.client.buy(account_id, # Buys the specified cryptocurrency.
                            total = total, # Buys the specified total (a portion of this total is used for fees) ...
                            currency = self.native_currency, # in the user's native currency.
                            payment_method = self.bank_payment_method_id) # Pays with the user's bank payment method.
        except RateLimitExceededError:
            print("The buy was too large. Please check your Account Limits on Coinbase or make a smaller investment.")
        except:
            print("The buy did not process. Please try again.")

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
        account_id = self.client.get_account(crypto)['id'] # Finds the wallet of the specified cryptocurrency.

        try:
            self.client.sell(account_id, # Sells the specified cryptocurreny.
                             amount = amount, # Sells the specified amount (a portion of this amount is used for fees) ...
                             currency = self.native_currency, # in the user's native currency.
                             payment_method = self.cash_payment_method_id) # Deposits the money into the user's Cash wallet.
        except:
            print("The sell did not process. Please try again.")

    def withdraw(self, amount):
        """
        Withdraws money from the user's Cash wallet and deposits the earnings into the user's bank payment method.

        amount: the amount to withdraw (in the user's native currency)
        """
        account_id = self.client.get_account(self.native_currency)['id'] # Finds the user's Cash wallet.

        try:
            self.client.withdraw(account_id, # Withdraws from the user's Cash wallet.
                                 amount = amount, # Withdraws the specified amount ...
                                 currency = self.native_currency, # in the user's native currency.
                                 payment_method = self.bank_payment_method_id) # Deposits the money into the user's bank payment method.
        except:
            print("The withdraw did not process. Please try again.")

    def get_cash_wallet_balance(self):
        """
        Gets the balance of the user's Cash wallet.

        return: the balance, as a float
        """
        balance = float(self.client.get_account(self.native_currency)['balance']['amount'])
        return balance

    def logout(self):
        """Logs out the user by revoking the access token."""
        self.client.revoke()
