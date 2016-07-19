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

def time_left(ms):
    s = ms / 1000
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return h, m, s

def get_pokemon(pk_user, pk_loc, max_steps):
	'''
	Args:
		pk_user: The user requesting the pokemon
		pk_loc: The location object
		steps: The amount of steps to take outwards from this location
	'''

	full_path = os.path.realpath(__file__)
	path, filename = os.path.split(full_path)
	pokemonsJSON = json.load(open(path + '/pokemon.json'))

	# get the aggregate area data
	pokemon, gyms, pokestops = cell_data.get_area_data(pk_user, pk_loc, max_steps)

	for poke in pokemon:
		other = LatLng.from_degrees(poke.Latitude, poke.Longitude)
		diff = other - origin
		difflat = diff.lat().degrees
		difflng = diff.lng().degrees
		time_to_hidden = poke.TimeTillHiddenMs
		left = '%d hours %d minutes %d seconds' % time_left(time_to_hidden)
		label = '%s [%s remaining]' % (pokemonsJSON[poke.pokemon.PokemonId - 1]['Name'], left)
		pokemons.append([poke.pokemon.PokemonId, label, poke.Latitude, poke.Longitude])

def main():

	users = settings.getSettings().users

	pk_user = None
	for u in users:

		# create a new user and check validity
		pk_user = user.User(u['username'], u['password'])
		break

	if pk_user.is_valid():
		print('User ' + str(pk_user) + ' has been created!')

	l = loc.Location()
	l.determine_location("Ashland, OH")
	print("coords", l.get_loc_coords())

	get_pokemon(pk_user, l, 1)

if __name__ == '__main__':
# Execute from command line
	main()

