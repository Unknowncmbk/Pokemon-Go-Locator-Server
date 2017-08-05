#!/usr/bin/python

# local imports
from settings import settings

# python modules
import json

'''
Note: This module serves as a handler of 'locations'. A location is something
with a GPS latitude and longitude.
'''

class Pokemon(object):
	def __init__(self, pokemon_id):
		self.pokemon_id = pokemon_id
		self.lat = 0
		self.lng = 0
		self.dist = 0
		self.expiration = 0

	def __init__(self, pokemon_id, lat, lng, expiration):
		self.pokemon_id = pokemon_id
		self.lat = lat
		self.lng = lng
		self.expiration = expiration
		self.dist = 0

	def __init__(self, pokemon_id, lat, lng, dist, expiration):
		self.pokemon_id = pokemon_id
		self.lat = lat
		self.lng = lng
		self.expiration = expiration
		self.dist = dist

	def __json__(self):
		'''
		Converts this object to JSON representation.
		'''
		json_object = {}
		json_object["pokemon_id"] = str(self.pokemon_id)
		json_object["lat"] = str(self.lat)
		json_object["lng"] = str(self.lng)
		json_object["distance"] = str(self.dist)
		json_object["time_left"] = str(self.expiration)
		return json.dumps(json_object, ensure_ascii=False)
		
	def set_location(self, lat, lng):
		'''
		Sets the location of the Pokemon.

		Args:
			lat: The latitutde of the Pokemon
			lng: The longtitude of the Pokemon
		'''
		self.lat = lat
		self.lng = lng

	def set_distance(self, dist):
		'''
		Sets the distance of the Pokemon.

		Args:
			dist: The distance
		'''
		self.dist = dist

	def set_expiration(self, expiration):
		'''
		Sets the expiration of the Pokemon

		Args:
			expiration: The expiration of the Pokemon
		'''
		self.expiration = expiration

def insert_pokemon(pokemon_id, lat, lng, expiration):
	'''
	Inserts the pokemon information into the database.

	Args:
		pokemon_id: The id of the pokemon
		lat: The latitude coordinate of the pokemon
		lng: The longitude coordinate of the pokemon
		expiration: The time in seconds until it expires.
	'''

	# Get new database instance
	db = settings.getDatabase()

	cur = db.cursor()
	query = '''INSERT IGNORE INTO pokemon_radar (pokemon_id, lat, lng, expiration) VALUES (%s, %s, %s, NOW() + INTERVAL %s SECOND) ON DUPLICATE KEY UPDATE expiration=NOW() + INTERVAL %s SECOND;'''
	data = ( int(pokemon_id), float(lat), float(lng), int(expiration), int(expiration) )
	cur.execute(query, data)

	# commit query
	db.commit()
	cur.close()

def get_pokemon(lat, lng, miles):
	'''
	Get all the pokemon at the specified location.

	Args:
		lat: the latitidue of the user
		lng: the longtitude of the user
		miles: the max miles to search

	Returns:
		A list of Pokemon objects within miles of the lat/lng.
	'''

	# Get new database instance
	db = settings.getDatabase()

	cur = db.cursor()
	query = '''SELECT pokemon_id, UNIX_TIMESTAMP(expiration) - UNIX_TIMESTAMP() as time_left, lat, lng, ( 3959 * acos( cos( radians(%s) ) * cos( radians( lat ) ) * cos( radians( lng ) - radians(%s) ) + sin( radians(%s) ) * sin( radians( lat ) ) ) ) AS distance FROM pokemon_radar WHERE expiration > NOW() HAVING distance < %s ORDER BY distance;'''
	data = (float(lat), float(lng), float(lat), int(miles))
	cur.execute(query, data)

	pokes = []

	for tup in cur:
		poke_id = int(tup[0])
		exp_in = int(tup[1])
		lat = float(tup[2])
		lng = float(tup[3])
		dist = float(tup[4])
		pokes.append(Pokemon(poke_id, lat, lng, dist, exp_in))

	# commit query
	db.commit()
	cur.close()

	return pokes