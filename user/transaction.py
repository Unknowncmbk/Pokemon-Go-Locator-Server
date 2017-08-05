#!/usr/bin/python

# local imports
from settings import settings

# python modules
import MySQLdb

'''
Note: This module serves as a handler of 'transactions', specifically ones that
populate pokemon data and ones that pull the data.
'''

def create_transaction(lat, lng):
    '''
    Creates the specified coordinate transaction in the database.

    Args:
        lat: The latitude of the request
        lng: The longtitude of the request
    '''

    # Get new database instance
    db = settings.getDatabase()

    cur = db.cursor()
    query = '''INSERT INTO pokemon_request (lat, lng) VALUES (%s, %s);'''
    data = (float(lat), float(lng))
    cur.execute(query, data)

    # commit query
    db.commit()
    cur.close()

def delete_transaction(trans_id):
    '''
    Deletes the transactions with the specified trans_id.

    Args:
        trans_id: The id of the transaction to delete
    '''
    # Get new database instance
    db = settings.getDatabase()

    cur = db.cursor()
    query = '''DELETE FROM pokemon_request WHERE id=%s;'''
    cur.execute(query, trans_id)

    # commit query
    db.commit()
    cur.close()

def pull_transaction():
    '''
    Pulls a transaction from the database in order to process it.
    '''
    # Get new database instance
    db = settings.getDatabase()

    cur = db.cursor()
    query = '''SELECT id, lat, lng FROM pokemon_request WHERE creation BETWEEN DATE_SUB(NOW(), INTERVAL 3 MINUTE) AND NOW() ORDER BY creation ASC;'''
    cur.execute(query)

    trans_id = 0
    lat = 0
    lng = 0
    for tup in cur:
        trans_id = int(tup[0])
        lat = float(tup[1])
        lng = float(tup[2])

    # commit query
    db.commit()
    cur.close()

    if trans_id > 0:
        delete_transaction(trans_id)

    return (lat, lng)