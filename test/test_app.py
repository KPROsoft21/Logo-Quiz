import os, json, pytest, time, unittest
from app import app
from flask import Flask, session, url_for
from app.helpers import login_user, get_game
from selenium import webdriver


#================================#

#disable CSRF for Testing
app.config['WTF_CSRF_ENABLED'] = False
app.config['SECRET_KEY'] = 'SECRET_KEY_SK'
new_user = {}

#================================#


# Create the flask application
@pytest.fixture(scope='module')
def test_client():
    flask_app = app
    client = flask_app.test_client()
    ctx = flask_app.app_context()
    ctx.push()
    yield client  
    ctx.pop()


# function to easily get a user from the users_file
@pytest.fixture(scope='module')
def get_user(username):
    with open('app/data/users.json') as users_file:
        users = json.load(users_file)
        for user in users['users']:
            if username == user['username']:
                return user


# function to easily get a user from the leaderboard_file
@pytest.fixture(scope='module')
def get_leaderboard_user(username):
    with open('app/data/leaderboard.json') as leaderboard_file:
        users = json.load(leaderboard_file)
        for user in users['users']:
            if username == user['username']:
                return user


# function to create a new user and add to 
# both the users_file and leaderboard_file
@pytest.fixture(scope='module')
def register_new_user():
    user = login_user('username', 'password', 'register')
    user = get_user('username')
    user_leaderboard = get_leaderboard_user('username')
    return (user, user_leaderboard)



#================================#
#    TEST ROUTES RESPONSES
#================================#


''' test routes '''

def test_routes_work(test_client):

    # ok
    response = test_client.get('/')
    assert response.status_code == 200
   
    # ok
    response = test_client.get('/leaderboard')
    assert response.status_code == 200

    # redirect
    response = test_client.get('/game')
    assert response.status_code == 302

    # redirect
    response = test_client.get('/logout')
    assert response.status_code == 302



#================================#
#    TEST LOGIN / REGISTER
#================================#

''' test login'''

def test_login_user():

    # test successful login returns a user
    user = login_user('sean', 'sean', 'login')
    assert type(user) is dict
    assert user['username'] == 'sean'


''' test incorrect details '''

def test_wrong_username_or_password():

    # no urser by that username exists
    user = login_user('nousername', 'nopassword', 'login')
    assert user == False

    # correct username but wrong password
    user = login_user('sean', 'wrongpassword', 'login')
    assert user == False



''' test register '''

def test_register_user_already_exists():

    # user already exists - cannot create new user
    user = login_user('sean', 'wrongpassword', 'register')
    assert user == False



#================================#


''' test game json file returned '''

def test_get_game():
    response = get_game()
    assert type(response) is list


#==================================#
    
    '''
        Due to using flask session variables in this flask
        app I cannot test the values of the variables
        during testing. 

        Instead I have decided to implement selenium
        with a webdriver using chrome browser to 
        simulate a full game. The chrome web driver
        is located in static/assets

        I will create a new user and test their before
        and after scores /results and leaderboard position.

        game list random shuffle was disabled during this 
        test in order to get the question corrrect to get 
        the end of the game.
    '''
 
#==================================#


# must pass on this test in order to not create 
# extra users everytime tests_file is run
def test_new_user():
    user = register_new_user()

    # check that the user has been added to the users_file
    assert user[0]['username'] == 'username'
    # check that user has been added to the leaderboard
    assert user[1]['username'] == 'username'



# test that the newly created users scores
# are all set to zero
def test_user_rating_before():
    new_user = get_user('username')

    assert new_user['last_played'] == 0
    assert new_user['times_played'] == 0
    assert new_user['best_time'] == 0
    assert new_user['best_score'] == 0
    assert new_user['best_rating'] == 0



#==================================#
    ''' CHROME BROWSER '''
#==================================#


class TestRunGame(unittest.TestCase):

    # init - set up the driver and window-size
    def setUp(self):
        self.driver = webdriver.Chrome('app/static/assets/chromedriver')
        self.driver.set_window_size(0,0)


    # completely run through the game
    def test_run_game(self):
        self.driver.get("http://127.0.0.1:5000/")
        time.sleep(1)

        # select elements on the index page
        login = self.driver.find_element_by_id('login_or_register-0')
        username = self.driver.find_element_by_id('username')
        password = self.driver.find_element_by_id('password')
        submit = self.driver.find_element_by_id('submit')
        
        
        # send clicks and input to inputs and submit
        login.click()
        username.send_keys('username')
        password.send_keys('password')
        submit.submit()
        time.sleep(1)


        #==================#

        # after login - press play game button
        play_game_button = self.driver.find_element_by_id('go-to-game')
        play_game_button.click()
        time.sleep(1)

        #==================#


        # on game page
        # iterate through the questions
        # temperarily disable shuffling in order to get answers correct
        game = get_game()
        for i in range(30):
            
            answer = self.driver.find_element_by_id('input')
            submit = self.driver.find_element_by_id('submit')

            answer.send_keys(game[i]['answer'])
            submit.submit()
            time.sleep(1)


        #==================#

    # game should be over and leaderboard displayed
    # shut down chrome 
    def tearDown(self):
        time.sleep(5)
        self.driver.get("http://127.0.0.1:5000/logout")
        self.driver.quit()



# run tests
if __name__ == '__main__':
    unittest.main()




#==================================#

'''
    Test that the user's leaderboard score has changed
    and that their user profile has changed.
'''

def test_user_rating_after():
    new_user = get_user('username')
    new_user_leaderboard = get_leaderboard_user('username')

    assert new_user['last_played'] != 0
    assert new_user['times_played'] != 0
    assert new_user['best_time'] != 0
    assert new_user['best_score'] != 0
    assert new_user['best_rating'] != 0

    assert new_user_leaderboard['best_time'] != 0
    assert new_user_leaderboard['best_score'] != 0
    assert new_user_leaderboard['best_rating'] != 0
