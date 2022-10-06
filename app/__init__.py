from flask import Flask
from config import Config
from flask_sslify import SSLify

'''
    initalise application and imported modules
    routes and errors are imported at the bottom
    as the app and config must be initalised first
'''

#=====================#


# initialise modules
app = Flask(__name__)
app.config.from_object(Config)
sslify = SSLify(app)

# import local modules
from app import routes, errors