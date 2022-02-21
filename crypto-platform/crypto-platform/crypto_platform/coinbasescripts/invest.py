"""
Scripts for initial investing and tax-loss harvesting.
"""

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
    pass