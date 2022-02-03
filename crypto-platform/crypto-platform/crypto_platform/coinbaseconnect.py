"""
Scripts for Coinbase Connect.
"""

import uuid
from flask import redirect, request
import requests
import json

client_id = 'ffa005fb7872cbeafb2bb86db26217f7088c3562b844612294b700bccee89d84' # The client ID of the registered Coinbase OAuth2 application
client_secret = 'c2eac670443511e9b227d2bf00537560e949afe1182835ca466adc3b18886cc6' # The client secret of the registered Coinbase OAuth2 application
redirect_uri = 'http://127.0.0.1:5000/redirect'
state = str(uuid.uuid4())

# Direct user to Coinbase login and authorization
def coinbase_login():
    auth_url = 'https://www.coinbase.com/oauth/authorize?response_type=code&client_id={}&redirect_uri={}&state={}&scope=wallet:accounts:read'.format(client_id, redirect_uri, state)
    return redirect(auth_url)

# Callback to Coinbase to get the access token
def coinbase_callback():
    login_response_code = request.args.get('code')
    login_response_state = request.args.get('state')

    post_data = {'grant_type': 'authorization_code', 'code': login_response_code, 'client_id': client_id, 'client_secret': client_secret, 'redirect_uri': redirect_uri } # The data for the callback to Coinbase
    
    if login_response_state == state: # If 'login_response_state' and 'state' do not match, the login response should not be trusted
        callback_response = requests.post('https://api.coinbase.com/oauth/token', data=post_data)
        access_token = callback_response.json()['access_token']
        refresh_token = callback_response.json()['refresh_token']
        return {'access_token': access_token, 'refresh_token': refresh_token}
    else:
        print('login_response_state and state do not match')

#
def coinbase_logout():
    print('placeholder')