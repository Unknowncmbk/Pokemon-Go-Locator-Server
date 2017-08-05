#!/usr/bin/python

# local imports
import pokemon
import cell_data
from user import transaction
from user import loc

# python modules
import time
import json
import Geohash
from flask import Flask
from flask import request

'''
Note: This module serves as the backend handler, serving app requests by
creating JSON responses.
'''

# how many steps do we query niantic for
DEFAULT_STEP_MAX = 10
# how many miles do we query our db for
DEFAULT_MILE_MAX = 3

# the cooldown for local requests
L_REQ_CD = 10
# the cooldown for fetch requests
F_REQ_CD = 300

# maps HOST -> last request from our DB
LOCAL_REQ = {}
# maps HOST -> last fetch request from niantic
FETCH_REQ = {}

app = Flask(__name__)

def can_local_request(req_ip, curr_time):
    '''
    Args:
        req_ip: The IP of the requester
        curr_time: The current time

    Returns:
        True if the requester can locally pull data. False otherwise.
    '''

    if req_ip in LOCAL_REQ:
        
        # grab the last request time
        if curr_time - LOCAL_REQ[req_ip] > L_REQ_CD:
            print('Host ' + str(req_ip) + ' can request locally!')
            return True
        else:
            print('Host ' + str(req_ip) + ' cannot request locally!')
            return False

    else:
        LOCAL_REQ[req_ip] = curr_time
        print('Adding host ' + str(req_ip) + ' to local request!')
        return True

def can_fetch_request(lat, lng, curr_time):
    '''
    Args:
        lat: The latititude of the fetch request
        lng: The longitude of the fetch request
        curr_time: The current time

    Returns:
        True if the requester can fetch data. False otherwise.
    '''

    # format the lat/lng to two decimals
    r_lat = "{0:.2f}".format(lat)
    r_lng = "{0:.2f}".format(lng)

    var = Geohash.encode(float(r_lat), float(r_lng))
    print('Lat/Lng pair of ' + str(lat) + '/' + str(lng) + ' rounds to ' + str(r_lat) + '/' +str(r_lng) + ' and hashes to ' + str(var))

    if var in FETCH_REQ:
        
        # grab the last request time
        if curr_time - FETCH_REQ[var] > F_REQ_CD:
            print('Can fetch request of ' + str(r_lat) + "/" + str(r_lng))

            # update it
            FETCH_REQ[var] = curr_time
            return True
        else:
            return False

    else:
        print('Can fetch request of ' + str(r_lat) + "/" + str(r_lng))

        FETCH_REQ[var] = curr_time
        return True

def build_local_request(lat, lng, radius):
    '''
    Builds the local request for pokemon data.

    Args:
        lat: The latitude of the request
        lng: The longitude of the request

    Returns:
        The JSON wrapped response with initial key 'result' and value 
        of array of pokemon data. If something went wrong, returns None.
    '''
    result = {}

    try:
        lat = float(lat)
        lng = float(lng)

        pokes_map = []
        pokes = pokemon.get_pokemon(lat, lng, radius)
        for p in pokes:
            pokes_map.append(p.__json__())

        result["result"] = pokes_map
        return json.dumps(result)
    except Exception as e:
        print('Exception ' + str(e))

    return None

@app.route('/req/<lat>/<lng>')
def get_pokemon(lat, lng):
    '''
    Args:
        lat: The latitude of the requested pokemon
        lng: The longitude of the requested pokemon

    Returns:
        A JSON object filled with pokemon data.
    '''

    try:
        lat = float(lat)
        lng = float(lng)

        # get the IP of the request
        req_ip = request.environ['REMOTE_ADDR']
        curr_time = time.time()

        result = None

        if can_fetch_request(lat, lng, curr_time):

            # create initial location request
            initial_loc = loc.Location()
            initial_loc.set_loc_coords(lat, lng, 0)
            initial_loc.default_lat = lat
            initial_loc.default_lng = lng

            # get all the locations in radius
            locs = cell_data.get_radius_locs(initial_loc, DEFAULT_STEP_MAX)

            if locs is not None and len(locs) > 0:

                for l in locs:

                    # fetch request data, by adding transaction to nexus
                    transaction.create_transaction(l.float_lat, l.float_lng)

        if can_local_request(req_ip, curr_time):

            # update time of their last request
            LOCAL_REQ[req_ip] = curr_time

            # build the local request
            result = build_local_request(lat, lng, DEFAULT_MILE_MAX)
            if result is not None:
                return result

    except Exception as e:
        print('Unable to grab lat/lng as floats: ' + str(e))

    return json.dumps(str({"result": result}))

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')