#!/usr/bin/python

# local imports
from settings import settings

# python modules
import requests
import json
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.adapters import ConnectionError
from requests.models import InvalidURL

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# session object for niantic
SESSION = requests.session()
SESSION.headers.update({'User-Agent': 'Niantic App'})
SESSION.verify = False

def get_access_token(username, password):
    '''
    Args:
        username: The username for the Pokemon Trainer Club
        password: The password associated with the username

    Returns:
        The access token generated for the Pokemon login.
    '''

    print('[!] login for: {}'.format(username))

    head = {'User-Agent': 'niantic'}
    r = SESSION.get(settings.URL_POKEMON_LOGIN, headers=head)
    jdata = json.loads(r.content)

    data = {
        'lt': jdata['lt'],
        'execution': jdata['execution'],
        '_eventId': 'submit',
        'username': username,
        'password': password,
    }

    r1 = SESSION.post(settings.URL_POKEMON_LOGIN, data=data, headers=head)

    ticket = None
    try:
        ticket = re.sub('.*ticket=', '', r1.history[0].headers['Location'])
    except Exception as e:
        if settings.DEBUG:
            print('Exception: ', e)
            print(r1.json()['errors'][0])
        return None

    data1 = {
        'client_id': 'mobile-app_pokemon-go',
        'redirect_uri': 'https://www.nianticlabs.com/pokemongo/error',
        'client_secret': 'w8ScCUXJQc6kXKw8FiOhd8Fixzht18Dq3PEVkUCP5ZPxtgyWsbTvWHFLm2wNY0JR',
        'grant_type': 'refresh_token',
        'code': ticket,
    }
    r2 = SESSION.post(settings.URL_LOGIN_OAUTH, data=data1)

    access_token = re.sub('&expires.*', '', r2.content)
    access_token = re.sub('.*access_token=', '', access_token)

    return access_token

def get_profile(access_token, api, useauth, *reqq):
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

    return api_req(api, access_token, req, useauth = useauth)

def get_session():
    return SESSION
