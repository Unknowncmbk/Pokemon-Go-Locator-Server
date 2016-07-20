#!/usr/bin/python

# local imports
from ext_api import niantic_api
from user import loc

# python modules
from s2sphere import *

def _get_cell_data(pk_user, pk_loc):
	'''
	Args:
		pk_user: The user requesting the data
		pk_loc: The parent location being requested

	Returns:
		A list of heartbeats where each element is geographical data about pokemon
		or other interests in the area.
	'''
	parent = CellId.from_lat_lng(LatLng.from_degrees(pk_loc.float_lat, pk_loc.float_lng)).parent(15)

	# get the heartbeat at specific location
	beat = niantic_api.get_heartbeat(pk_user.session_url, pk_user.session_token, pk_loc, pk_user.profile)
	
	# the list of heart beats
	heartbeats = [beat]

	# get relative data points near location
	for child in parent.children():

		# get the lat / lng on the grid
		latlng = LatLng.from_point(Cell(child).get_center())

		# create new location to query
		new_loc = loc.Location()
		new_loc.set_loc_coords(latlng.lat().degrees, latlng.lng().degrees, 0)

		# get heartbeat of child location
		heartbeats.append(niantic_api.get_heartbeat(pk_user.session_url, pk_user.session_token, new_loc, pk_user.profile))

	return heartbeats

def _parse_cell_data(heartbeats):
	'''
	Parses the given cell data, getting the pokemon information.

	Args:
		heartbeats: The heartbeats of specific locations

	Returns:
		A tuple of (pokemon, gyms, pokestops) where each element in
		in the tuple is a list.
	'''

	pokemon = []
	gyms = []
	pokestops = []

	# hash set for pokemon that we've seen
	seen = set([])

	for h in heartbeats:
		try:
			for cell in h.cells:
				for wild in cell.WildPokemon:
					hash = wild.SpawnPointId + ':' + str(wild.pokemon.PokemonId)
					if (hash not in seen):
						pokemon.append(wild)
						seen.add(hash)
				if cell.Fort:
					for Fort in cell.Fort:
						if Fort.Enabled == True:
							if Fort.GymPoints:
								gyms.append([Fort.Team, Fort.Latitude, Fort.Longitude])
							elif Fort.FortType:
								pokestops.append([Fort.Latitude, Fort.Longitude])
		except AttributeError:
			break
	
	return pokemon, gyms, pokestops

def get_area_data(pk_user, pk_loc, max_steps):
	'''
	Get all the pokemon data for the specific location and max steps around
	that location.

	Args:
		pk_user: The user requesting the pokemon
		pk_loc: The location object
		steps: The amount of steps to take outwards from this location

	Returns:
		A tuple of (pokemon, gyms, pokestops) where each element in
		in the tuple is a list.
	'''

	# result sets for area data
	res_pokemon = []
	res_gym = []
	res_pokestop = []

	# origin of the map
	origin = LatLng.from_degrees(pk_loc.float_lat, pk_loc.float_lng)

	print("Initial lat: ", pk_loc.float_lat)
	print("Initial lng: ", pk_loc.float_lng)

	# current map information
	steps = 0
	steplimit = int(max_steps)
	pos = 1
	x   = 0
	y   = 0
	dx  = 0
	dy  = -1

	while steps < steplimit ** 2:

		print("cell data lat: ", pk_loc.float_lat)
		print("cell data lng: ", pk_loc.float_lng)
		# grab all the heart beats for this location
		heartbeats = _get_cell_data(pk_user, pk_loc)
		print("heartbeats", heartbeats)

		if heartbeats is not None and len(heartbeats) > 0:

			# parse the data
			pokemon, gyms, pokestops = _parse_cell_data(heartbeats)

			# add data to results above
			if pokemon is not None and len(pokemon) > 0:
				res_pokemon.extend(pokemon)

			if gyms is not None and len(gyms) > 0:	
				res_gym.extend(gyms)

			if pokestops is not None and len(pokestops) > 0:
				res_pokestop.extend(pokestops)

		#Scan location math
		if (-steplimit/2 < x <= steplimit/2) and (-steplimit/2 < y <= steplimit/2):
			pk_loc.set_loc_coords((x * 0.0025) + pk_loc.default_lat, (y * 0.0025 ) + pk_loc.default_lng, 0)
		if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
			dx, dy = -dy, dx
		x, y = x+dx, y+dy
		steps +=1
		print("Completed:", ((steps + (pos * .25) - .25) / steplimit**2) * 100, "%")

	return res_pokemon, res_gym, res_pokestop

