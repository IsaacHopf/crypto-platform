from coinbase.wallet.client import OAuthClient

class User(object):
    """Represents the user of our platform."""

    def __init__(self, tokens):
        self.client = OAuthClient(tokens['access_token'], tokens['refresh_token'])
        self.payment_method = self.__select_payment_method()
        self.id = self.client.get_current_user()['id']

    def __select_payment_method(self):
        """Selects the user's primary payment method if it exists."""
        payment_methods = self.client.get_payment_methods()

        for payment_method in payment_methods['data']:
            if payment_method['primary_buy'] == True & payment_method['allow_withdraw'] == True & payment_method['allow_deposit'] == True:
                return payment_method['id']

        # If the User hasn't added a payment method
        print("please add your preferred payment method")

    def buy(self, amount, currency):
        """Buys cryptocurrency using the User's account."""
        self.client.buy(self.id, amount=amount, currency=currency, payment_method=self.payment_method)

    def sell(self, amount, currency):
        """Sells cryptocurrency using the User's account."""
        self.client.sell(self.id, amount=amount, currency=currency, payment_method=self.payment_method)

    def logout():
        """Logs out the user by revoking the access token."""
        self.client.revoke()
