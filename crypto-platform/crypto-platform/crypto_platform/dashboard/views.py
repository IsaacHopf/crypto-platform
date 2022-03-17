"""
Routes and views for the dashboard pages.
"""

from flask import Blueprint, render_template

from crypto_platform import connect
from crypto_platform.dashboard import invest
from crypto_platform.dashboard.User import User

dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard', 
                      template_folder='templates',
                      static_folder='static')

@dashboard.route('/')
def home():
    """Renders the redirect page and handles coinbase_callback."""
    tokens = connect.coinbase_callback()

    global user
    user = User(tokens)

    return render_template(
        'dashboard.html',
        title='Dashboard',
        #year=datetime.now().year,
        message='Your application description page.'
    )

@dashboard.route('/testscripts')
def testscripts():
    invest.process_investments(user)

    return render_template(
        'dashboard.html',
        title='Dashboard',
        year=datetime.now().year
    )

