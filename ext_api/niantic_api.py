#!/usr/bin/python

# local imports
from settings import settings
from session import session
from user import loc
import pokemon_pb2

# python modules
import time

from s2sphere import *
from google.protobuf.internal import encoder

def encode(cellid):
    output = []
    encoder._VarintEncoder()(output.append, cellid)
    return ''.join(output)

def request_data(session_url, session_token, pk_loc, *mehs, **kw):
    tries = 10

    while tries > 0:
        try:
            p_req = pokemon_pb2.RequestEnvelop()
            p_req.rpc_id = 1469378659230941192

            p_req.unknown1 = 2

            p_req.latitude, p_req.longitude, p_req.altitude = pk_loc.get_loc_coords()

            p_req.unknown12 = 989

            if 'useauth' not in kw or not kw['useauth']:
                p_req.auth.provider = 'ptc'
                p_req.auth.token.contents = session_token
                p_req.auth.token.unknown13 = 14
            else:
                p_req.unknown11.unknown71 = kw['useauth'].unknown71
                p_req.unknown11.unknown72 = kw['useauth'].unknown72
                p_req.unknown11.unknown73 = kw['useauth'].unknown73

            for meh in mehs:
                p_req.MergeFrom(meh)

            protobuf = p_req.SerializeToString()

            r = session.get_session().post(session_url, data=protobuf, verify=False)

            p_ret = pokemon_pb2.ResponseEnvelop()
            p_ret.ParseFromString(r.content)

            if settings.DEBUG:
                print("REQUEST:")
                print(p_req)
                print("Response:")
                print(p_ret)
                print("\n\n")

            time.sleep(2)
            return p_ret
        except Exception, e:
            if settings.DEBUG:
                print('Exception occurred in niantic_api.py#request_data()')
                print(e)
            return None

        tries = tries - 1

def get_profile(session_token, session_url, pk_loc, useauth, *reqq):
    req = pokemon_pb2.RequestEnvelop()

    req1 = req.requests.add()
    req1.type = 2
    if len(reqq) >= 1:
        req1.MergeFrom(reqq[0])

    req2 = req.requests.add()
    req2.type = 126
    if len(reqq) >= 2:
        req2.MergeFrom(reqq[1])

    req3 = req.requests.add()
    req3.type = 4
    if len(reqq) >= 3:
        req3.MergeFrom(reqq[2])

    req4 = req.requests.add()
    req4.type = 129
    if len(reqq) >= 4:
        req4.MergeFrom(reqq[3])

    req5 = req.requests.add()
    req5.type = 5
    if len(reqq) >= 5:
        req5.MergeFrom(reqq[4])

    return request_data(session_url, session_token, pk_loc, req, useauth = useauth)

def get_request_url(access_token, api_url):

    # create empty location
    l = loc.Location()

    tries = 10
    while tries > 0:

        p_ret = get_profile(access_token, api_url, l, None)
        try:
            return ('https://%s/rpc' % p_ret.api_url)
        except:
            print("Retrying to get profile...")

        tries = tries - 1

def getNeighbors(lat, lng):
    origin = CellId.from_lat_lng(LatLng.from_degrees(lat, lng)).parent(15)
    walk = [origin.id()]
    # 10 before and 10 after
    next = origin.next()
    prev = origin.prev()
    for i in range(10):
        walk.append(prev.id())
        walk.append(next.id())
        next = next.next()
        prev = prev.prev()
    return walk

def get_heartbeat(api_endpoint, access_token, pk_loc, response):
    m4 = pokemon_pb2.RequestEnvelop.Requests()
    m = pokemon_pb2.RequestEnvelop.MessageSingleInt()
    m.f1 = int(time.time() * 1000)
    m4.message = m.SerializeToString()
    m5 = pokemon_pb2.RequestEnvelop.Requests()
    m = pokemon_pb2.RequestEnvelop.MessageSingleString()
    m.bytes = "05daf51635c82611d1aac95c0b051d3ec088a930"
    m5.message = m.SerializeToString()
    walk = sorted(getNeighbors(pk_loc.float_lat, pk_loc.float_lng))
    m1 = pokemon_pb2.RequestEnvelop.Requests()
    m1.type = 106
    m = pokemon_pb2.RequestEnvelop.MessageQuad()
    m.f1 = ''.join(map(encode, walk))
    m.f2 = "\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
    m.lat = pk_loc.coords_lat
    m.long = pk_loc.coords_lng
    m1.message = m.SerializeToString()

    # get the response from niantic
    response = get_profile(
        access_token,
        api_endpoint,
        pk_loc,
        response.unknown7,
        m1,
        pokemon_pb2.RequestEnvelop.Requests(),
        m4,
        pokemon_pb2.RequestEnvelop.Requests(),
        m5)

    if response is None:
        return

    payload = response.payload[0]
    heartbeat = pokemon_pb2.ResponseEnvelop.HeartbeatPayload()
    heartbeat.ParseFromString(payload)
    return heartbeat
