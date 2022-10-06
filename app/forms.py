from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired, ValidationError

'''
    using flask-wtf to create and manage forms, validation and CSRF protection
'''

#=====================#


# Login / Register Form
class LoginForm(FlaskForm):
    
    # Fields - require some validation
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    login_or_register = RadioField('login or register', choices=[('login','login'),('register','register')], validators=[DataRequired()])
    submit = SubmitField('submit')

    '''
        below functions only need to check for sufficent character length
        when creating a username and password.
    '''

    # username
    def validate_username(self, username):
        if len(username.data) < 4:
            raise ValidationError('username must be longer than 4 characters')

    # passsword
    def validate_password(self, password):
        if len(password.data) < 4:
            raise ValidationError('password must be longer than 4 characters')



#=====================#

'''
    the answer form does not require validation at this point,
    as it will be handling in a helper function after a post request
'''

# Answer / Questions Form
class AnswerForm(FlaskForm):

    # fields - no validation needed
    answer = StringField('answer')
    submit = SubmitField('submit')


#=====================#
