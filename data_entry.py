#!/usr/bin/python

# local imports
from settings import settings

# python modules
import json
import os

def insert_pokemon(pokemon_id, name):
	# Get new database instance
    db = settings.getDatabase()

    cur = db.cursor()
    query = '''INSERT INTO pokemon (id, name) VALUES (%s, %s);'''
    data = (int(pokemon_id), str(name))
    cur.execute(query, data)

    # commit query
    db.commit()
    cur.close()

def main():

	full_path = os.path.realpath(__file__)
	path, filename = os.path.split(full_path)
	pokemonsJSON = json.load(open(path + '/pokemon.json'))

	for pokemon in pokemonsJSON:
		pokemon_id = pokemon['Number']
		name = pokemon['Name']
		print("#" + str(pokemon_id) + " is " + str(name))
		insert_pokemon(pokemon_id, name)

	# close db connection
	settings.getSettings().close()

if __name__ == '__main__':
# Execute from command line
	main()

