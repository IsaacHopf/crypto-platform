"""
Scripts for Coinbase Connect that handle user authentication and authorization.
"""

import uuid
from flask import redirect, request
import requests
import json
import time

client_id = 'ffa005fb7872cbeafb2bb86db26217f7088c3562b844612294b700bccee89d84' # The client ID of the registered Coinbase OAuth2 application.
client_secret = 'c2eac670443511e9b227d2bf00537560e949afe1182835ca466adc3b18886cc6' # The client secret of the registered Coinbase OAuth2 application.
redirect_uri = 'http://127.0.0.1:5000/dashboard'
state = str(uuid.uuid4())
scope = 'wallet:accounts:read,wallet:payment-methods:read,wallet:buys:create,wallet:buys:read,wallet:sells:create,wallet:sells:read,wallet:withdrawals:create,wallet:user:read,wallet:user:email'

def coinbase_login():
    """Directs the user to login through Coinbase."""
    auth_url = 'https://www.coinbase.com/oauth/authorize?response_type=code&client_id={}&redirect_uri={}&state={}&scope={}'.format(client_id, redirect_uri, state, scope)
    return redirect(auth_url)

def coinbase_callback():
    """Calls back to Coinbase to get the access token and refresh token."""
    login_response_code = request.args.get('code')
    login_response_state = request.args.get('state')

    if login_response_code == None or login_response_state == None: # If the login reponses are None, then the User did not log in.
        raise AttributeError('User has not logged in!')
    else:
        if login_response_state == state:
            # If login response is trustworthy
            post_data = {'grant_type': 'authorization_code', 'code': login_response_code, 'client_id': client_id, 'client_secret': client_secret, 'redirect_uri': redirect_uri } # The data for the callback to Coinbase
            callback_response = requests.post('https://api.coinbase.com/oauth/token', data=post_data)
            access_token = callback_response.json()['access_token']
            refresh_token = callback_response.json()['refresh_token']
            return {'access_token': access_token, 'refresh_token': refresh_token}
        else:
            # If login response is untrustworthy
            return coinbase_login()