import time, math
from app import app
from flask import render_template, redirect, url_for, session, request, flash
from app.forms import LoginForm, AnswerForm
from app.helpers import get_leaderboard,  login_user, create_session_variables, reset_variables, set_session_scores

'''
    In an attempt to keep each route as succinct as possible,
    I have created and imported helper function from helper.py

    This application relies heavily on flask session variables and data
    from JSON files which will be read and written to. 
'''


#=====================#


'''
    index serves as both a user login/register and
    user home page from which to start a new game 
'''


# index
@app.route('/', methods=['GET', 'POST'])
def index():

    # when a logged in user returns to the index page
    # a new game should be created - reset relevent variables
    if 'user' in session:
        reset_variables()

    # if login_form passes validation
    login_form = LoginForm()
    if login_form.validate_on_submit():

        # call login_user function to either validate user or register new user
        # form username and password are passed to helper function
        # will return the user dict is valid - else will retun false if login failed
        user = login_user(login_form.username.data, login_form.password.data, login_form.login_or_register.data)
        
        # if user is false then password must be incorrect
        if not user:

            if (login_form.login_or_register.data == 'register'):
                flash('That username is already in use')
            else:
                flash('Incorrect username or password')
            return redirect(url_for('index'))

        # otherwise the user is logged in and all session variables will be created 
        else:
            create_session_variables(user)
            return redirect(url_for('index'))
        

    # default - render index.html
    return render_template('index.html', login_form=login_form, endpoint="index")


#=====================#


'''
    the game route works by having all scores set to 0 before starting,
    the game questions are initialised beforehand when a user in on the 
    index page and stored in a session['game'] variable. Each time the 
    index increases, that will be used to get the question from session['game].

    users should NOT be able to go back to a previous question or access the page
    directly, users scores will be displayed and saved upon completion of the game,
    if a user quits, they forfeit that game. Helper functions are used extensively 
    to track, reset and save user scores.
'''


# game
@app.route('/game', methods=['GET', 'POST'])
def game():

    # protect route - if user is not logged in 
    # they will be redirect back to the index page
    if not 'user' in session:
        return redirect(url_for('index'))


    # if a new game has begun start the timer
    if session['new_game'] == 1:
        session['new_game'] = 0
        session['start_time'] = time.time()


    
    # Answer Checking
    answer_form = AnswerForm()
    if answer_form.validate_on_submit():

        # if the answer is correct - increase the correct score
        if session['game'][session['index'] - 1]['answer'] ==  answer_form.answer.data.lower():
            session['current_score'] += 1
        
        # otherwise - it must be empty or a wrong answer
        else:
            if not answer_form.answer.data:
                # if answer is empty
                flash(f'answer field cannot be empty')
            else:
                # if answer is wrong
                flash(f'Incorrect answer! You guessed {answer_form.answer.data}, try again..')

            # return the same question
            # prevent index increasing
            session['index'] -= 1
            return redirect(url_for('game'))


    # If the game is over 
    # Write users scores to json file to save them
    # then redirect to leaderboard to show results
    if session['index'] >= 30:
        set_session_scores()
        return redirect(url_for('leaderboard'))


    # increase index pagination to show ther next question logo
    # continue to track the players time - pass time to jinja
    session['index'] += 1
    session['current_time'] = round(time.time() - session['start_time'])


    # default - render game.html
    # if a question is passed - a new question will render
    return render_template('game.html', endpoint="game", answer_form=answer_form)


#=====================#


'''
    leaderboard is accesible for both logged in and
    anonymous users, a new instance of the leaderboard
    is required for each render in case of an update.
    A helper function does this logic.  
'''


# leaderboard
@app.route('/leaderboard')
def leaderboard():

    # if the game is ended early by the user
    # end the game and reset variables
    if 'user' in session:
        set_session_scores()

    # get a new instance of the Leaderboard
    leaderboard = get_leaderboard()

    # default - return leaderboard.html
    return render_template('leaderboard.html', leaderboard=leaderboard, endpoint="leaderboard")


#=====================#


'''
    logs out user and clears all session variables
    redirects back to login / index page
'''


# logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


#=====================#