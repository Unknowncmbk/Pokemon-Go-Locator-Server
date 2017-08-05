#!/usr/bin/python

# local imports
from user import transaction
from user import user
from user import loc
from settings import settings
import pokemon
import cell_data

# python modules
import argparse
import time
import sys

'''
Note: This module serves as a slave to handle location requests.
'''

def access_data(pk_user, pk_loc):
	'''
	Args:
		pk_user: The user requesting the pokemon
		pk_loc: The location object
		steps: The amount of steps to take outwards from this location

	Returns:
		A list of pokemon at the specified location and within max_steps.
	'''

	# get the aggregate area data
	pk_data, pk_gyms, pk_stops = cell_data.get_area_data(pk_user, pk_loc)

	for p in pk_data:
		pk_id = p.pokemon.PokemonId
		lat = p.Latitude
		lng = p.Longitude
		time_to_hidden = p.TimeTillHiddenMs
		seconds = int(p.TimeTillHiddenMs / 1000.0)

		print('[+] Inserting #' + str(pk_id) + ' at lat=' + str(lat) + ', lng=' + str(lng))

		pokemon.insert_pokemon(pk_id, lat, lng, seconds)

	return pk_data


def handle_requests(pk_user):
	'''
	Handles the requests for the specified user.

	Args:
		pk_user: The authentified user
	'''
	while True:

		# pull a transaction
		lat, lng = transaction.pull_transaction()
		if lat != 0 and lng != 0:

			print('[+] ' + str(pk_user.username) + ' handling fetch transaction of lat=' + str(lat) + ', lng=' + str(lng))

			# create location object
			pk_loc = loc.Location()
			pk_loc.default_lat = lat
			pk_loc.default_lng = lng
			pk_loc.set_loc_coords(lat, lng, 0)

			# access the data
			access_data(pk_user, pk_loc)

		# if settings.DEBUG:
		# 	print('Sleeping for ' + str(pk_user.username) + '...')

		# # sleep between requests
		# time.sleep(1)


if __name__ == "__main__":
	# if called as the main file

	parser = argparse.ArgumentParser()
	parser.add_argument("-u", "--username", help="PTC Username", required=True)
	parser.add_argument("-p", "--password", help="PTC Password", required=True)
	args = parser.parse_args()

	# create new user to handle requests
	pk_user = user.User(args.username, args.password)
	if pk_user.is_valid():
		handle_requests(pk_user)
	else:
		print('Error: Unable to verify the credentials of ' + str(args.username))
		sys.exit()