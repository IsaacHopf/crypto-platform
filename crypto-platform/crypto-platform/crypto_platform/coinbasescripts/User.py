from coinbase.wallet.client import OAuthClient

class User(object):
    """description of class"""

    def __init__(self, tokens):
        self.client = OAuthClient(tokens['access_token'], tokens['refresh_token'])
        print(self.client.get_current_user())

    #    self.payment_method = select_payment_method()
    #    self.deposit_method = select_deposit_method()


    ## Returns the id of the primary payment method for buying
    #def select_payment_method(self):
    #    payment_methods = self.client.get_payment_methods()

    #    for payment_method in payment_methods['data']:
    #        if payment_method['primary_buy'] == true:
    #            return payment_method['id']

    #    print("please add a payment method")

    ## Returns the id of the primary payment method for selling
    #def select_deposit_method(self): 
    #    payment_methods = self,client.get_payment_methods()

    #    for payment_method in payment_methods['data']:
    #        if payment_method['primary_sell'] == true:
    #            return payment_method['id']

    #    print("please add a payment method")