#!/usr/bin/python

# local imports
from settings import settings
from session import session
from ext_api import niantic_api
from ext_api import pokemon_pb2
from user import user
from user import loc
import cell_data

# python modules
from datetime import datetime
from s2sphere import *
import os
import json

numbertoteam = {0: "Gym", 1: "Mystic", 2: "Valor", 3: "Instinct"}

def insert_pokemon(pokemon_id, lat, lng, expiration):
	# Get new database instance
	db = settings.getDatabase()

	cur = db.cursor()
	query = '''INSERT INTO pokemon_radar (pokemon_id, lat, lng, expiration) VALUES (%s, %s, %s, NOW() + INTERVAL %s SECOND);'''
	data = (int(pokemon_id), float(lat), float(lng), expiration)
	cur.execute(query, data)

	# commit query
	db.commit()
	cur.close()


def time_left(ms):
    s = ms / 1000
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return h, m, s

def access_data(pk_user, pk_loc, max_steps):
	'''
	Args:
		pk_user: The user requesting the pokemon
		pk_loc: The location object
		steps: The amount of steps to take outwards from this location
	'''

	# get the aggregate area data
	pokemon, gyms, pokestops = cell_data.get_area_data(pk_user, pk_loc, max_steps)

	for poke in pokemon:
		poke_id = poke.pokemon.PokemonId
		time_to_hidden = poke.TimeTillHiddenMs
		seconds = int(poke.TimeTillHiddenMs / 1000.0)
		
		insert_pokemon(poke.pokemon.PokemonId, poke.Latitude, poke.Longitude, seconds)

def main():

	users = settings.getSettings().users

	pk_user = None
	for u in users:

		# create a new user and check validity
		pk_user = user.User("Unknowncmbk", "KyraKay0693")
		#pk_user = user.User(u['username'], u['password'])
		break

	if pk_user.is_valid():
		print('User ' + str(pk_user) + ' has been created!')

	l = loc.Location()
	l.determine_location("Ashland, OH")
	print("coords", l.get_loc_coords())

	access_data(pk_user, l, 1)

if __name__ == '__main__':
# Execute from command line
	main()

