from app import app
from flask import render_template, request, url_for
import json


'''
    Handle 404, 500 Errors
'''

#=====================#


# handle 404 error - page not found
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html', endpoint="404"), 404


#=====================#


# handle 500 error - internal server error
@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html', endpoint="500"), 500


#=====================#