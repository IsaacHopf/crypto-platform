"""
This script runs the crypto_platform application using a development server.
"""

from os import environ
from crypto_platform import app

if __name__ == '__main__':
    app.run(debug=True)
    #HOST = environ.get('SERVER_HOST', 'localhost')
    #try:
    #    PORT = int(environ.get('SERVER_PORT', '5555'))
    #except ValueError:
    #    PORT = 5555
    #app.run(HOST, PORT)
