"""
Scripts for Coinbase Connect that handle user authentication and authorization.
"""

import uuid
from flask import redirect, request
import requests
import json
import time

client_id = 'ffa005fb7872cbeafb2bb86db26217f7088c3562b844612294b700bccee89d84' # The client ID of the registered Coinbase OAuth2 application
client_secret = 'c2eac670443511e9b227d2bf00537560e949afe1182835ca466adc3b18886cc6' # The client secret of the registered Coinbase OAuth2 application
redirect_uri = 'http://127.0.0.1:5000/redirect'
state = str(uuid.uuid4())
scope = 'wallet:accounts:read,wallet:payment-methods:read,wallet:buys:create,wallet:buys:read,wallet:sells:create,wallet:sells:read'

def coinbase_login():
    """Directs the user to login through Coinbase."""
    auth_url = 'https://www.coinbase.com/oauth/authorize?response_type=code&client_id={}&redirect_uri={}&state={}&scope={}'.format(client_id, redirect_uri, state, scope)
    return redirect(auth_url)

def coinbase_callback():
    """Calls back to Coinbase to get the access token and refresh token."""
    login_response_code = request.args.get('code')
    login_response_state = request.args.get('state')

    post_data = {'grant_type': 'authorization_code', 'code': login_response_code, 'client_id': client_id, 'client_secret': client_secret, 'redirect_uri': redirect_uri } # The data for the callback to Coinbase
    
    if login_response_state == state: # If 'login_response_state' and 'state' do not match, the login response should not be trusted
        callback_response = requests.post('https://api.coinbase.com/oauth/token', data=post_data)
        access_token = callback_response.json()['access_token']
        refresh_token = callback_response.json()['refresh_token']
        return {'access_token': access_token, 'refresh_token': refresh_token}
    else:
        print('redirect user back to home page and say an error has occurred, please try logging in again')

def getPrices():
    while True:
        response = requests.get('https://api.coinbase.com/v2/prices/BTC-USD/spot')
        data = response.json()
        currency = data["data"]["base"]
        price = data["data"]["amount"]
        print(f"Currency: {currency} Price: {price}")
        time.sleep(5)
