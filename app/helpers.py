import json, time, math 
from random import shuffle
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, redirect
from datetime import datetime


'''
	This helper file serves as a location for all functions which will be 
	called upon by tthe relevent route functions.

	Most operation involve reading and wrting to json files or 
	setting session variables.
'''


#============================================#


'''
	This is a multiple purpose function which will both check for an
	existing user - if that user is found it will check their credentials.

	And if no user is found it will create a new user and add them to both
	the leaderboard and users file.
'''


def login_user(username, password, choice): 

	with open('app/data/users.json', 'r+') as users_file:
		users = json.load(users_file)

		# check for existing user
		for user in users['users']:

			# if the username exists then check the password matches
			if user['username'] == username.lower():

				# if the user was registering
				# then the username must be taken
				if choice == 'register':
					return False

				# using werkzeug.security function
				if check_password_hash(user['password'], password):
					# if password is ok return the user
					return user
				# if password is incorrect - return false
				return False

		# if the user was logging in
		# then they have entered a username 
		# that does not exist
		if choice == 'login':
			return False

		# if no user is found, create a new user
		# and save their username and password
		with open('app/data/user.json') as user_file:
			user = json.load(user_file)
			user['username'] = username.lower()

			# using werkzeug.security function to hash the password
			user['password'] = generate_password_hash(password)

			# append the user to the users list
			users['users'].append(user)


			# also at the time of user creation 
			# add the new user to the leaderboard
			add_to_leaderboard(user['username'])

			# seek file to overwrite
			# Add new user to the users_file
			# return the new user
			users_file.seek(0)
			json.dump(users, users_file)
			return user

	
#============================================#


'''
	adding the user to the leaderboard at the time of user creation
	means they dont have to be added at a later stage, better to
	get it out of the way now, less code later.
'''


def add_to_leaderboard(username):
	with open('app/data/leaderboard.json', 'r+') as leaderboard_file:
		leaderboard = json.load(leaderboard_file)

		# create a user model for the leaderboard
		user = {
			"username": username,
			"best_time": 0, 
			"best_score": 0, 
			"best_rating": 0, 
		}

		# append the user to the leaderboard
		leaderboard['users'].append(user)

		# seek the file to overwrite
		# write to the json file
		leaderboard_file.seek(0)
		json.dump(leaderboard, leaderboard_file)

	
#============================================#


'''
	this function will return a sorted list of users from the leaderboard file,
	it will also find a user in the leaderboard and if they have 
	a new best rating, update the leaderboard, also return but not
	written to file is the last played games results appended to the
	list only in memory.
'''


def get_leaderboard():
	with open('app/data/leaderboard.json', 'r+') as leaderboard_file:
		leaderboard = json.load(leaderboard_file)

		# if the user is already on the leaderboard
		# and they have a new best score
		# update the users record
		if 'user' in session:

			# find the user
			for user in leaderboard['users']:
				if session['user'] == user['username']:

					# only if the have a new best rating should the leaderboard
					# be written to as its a top score - not last played
					if session['best_rating'] > user['best_rating']:
						user['best_time'] = session['best_time']
						user['best_score'] = session['best_score']
						user['best_rating'] = session['best_rating']
						break

			# overwrite the json file
			leaderboard_file.seek(0)
			json.dump(leaderboard, leaderboard_file)


			# Add current user scores to leaderboard - only if its not their first time playing
			# but dont write to file - this is for seeing last played scores against best scores
			# this will be returned to the leaderboard route and only held in memory
			if session['times_played'] > 1 and session['current_rating'] != 0:
				current_user = {
					"username": "LAST PLAYED",
					"best_time": session['current_time'], 
					"best_score": session['current_score'], 
					"best_rating": session['current_rating'], 
				}
				leaderboard['users'].append(current_user)


		# lamda learned from w3resource.com
		# sort the leaderboard by highest rating
		leaderboard['users'].sort(key=lambda x: x['best_rating'], reverse=True)
		return leaderboard['users']

	
#============================================#


'''
	when on the index page this function will get the 
	game data and shuffle the list in preperation for a new game
'''


def get_game():
    with open('app/data/game.json') as game_file:
        game = json.load(game_file)
        shuffle(game['game'])
        return game['game']

	
#============================================#


'''
	when on the index page all current variables should be reset,
	this happens before every game including login
'''

def reset_variables():
	session['game'] = get_game()
	session['index'] = 0
	session['current_time'] = 0
	session['current_score'] = 0
	session['current_rating'] = 0
	session['new_game'] = 1
	session['start_time'] = 0

	
#============================================#


'''
	this function will create session variables from the users 
	saved data and will be used throughout the game only being updated
	after a game has been completed.
'''

def create_session_variables(user):
	session['user'] = user['username']
	session['last_played'] = user['last_played']
	session['times_played'] = user['times_played']
	session['best_time'] = user['best_time']
	session['best_score'] = user['best_score']
	session['best_rating'] = user['best_rating']

	
#============================================#


'''
	after a game is complete, we must calculate the scores, time, 
	and compare current against best ratings. Some variables need
	to bee converted to a format suitable for json both for for writing
	and also for reading, such as when a user logs back in it must be 
	convertable back to a readable format. 
'''


def set_session_scores():
	
	# only if a game has been started should scores be accessed
	if session['current_score'] > 0:

		# must convert datetime to string - cannot serialize datetime to JSON
		session['last_played'] = datetime.strftime(datetime.utcnow(), '%a, %d %b, %H:%M') 
		session['times_played'] += 1

		# game time elapsed is equal to starting time - current time
		session['current_time'] = round(time.time() - session['start_time'])
		

		# final rating is based on:
		# answers correct * 1000 minus time * 10
		session['current_rating'] = (session['current_score'] * 1000) - (session['current_time'] * 10)


		# only if the last game played if better than the best score
		# should the best scores by updated
		if session['best_rating'] < session['current_rating']:
			session['best_time'] = session['current_time']
			session['best_score'] = session['current_score']
			session['best_rating'] = session['current_rating']
		
		# write new data to user dict for next login
		write_new_scores()

	
#============================================#


'''
	after a game has been completed, in order to persist data for
	the next login of the user, their data will be written to the
	users json file.
'''


def write_new_scores():
	with open('app/data/users.json', 'r+') as users_file:
		users = json.load(users_file)
		
		for user in users['users']:
			# find the user by username
			if session['user'] == user['username']:
				user['last_played'] = session['last_played']
				user['times_played'] = session['times_played']
				user['best_time'] = session['best_time']
				user['best_score'] = session['best_score']
				user['best_rating'] = session['best_rating']

		# overwrite users file with updated data
		users_file.seek(0)
		json.dump(users, users_file)

	
#============================================#




