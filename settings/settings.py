#!/usr/bin/python

# python modules
import json
import socket
import MySQLdb

# The URL to the Pokemon Login auth
URL_POKEMON_LOGIN = 'https://sso.pokemon.com/sso/login?service=https%3A%2F%2Fsso.pokemon.com%2Fsso%2Foauth2.0%2FcallbackAuthorize'
URL_LOGIN_OAUTH = 'https://sso.pokemon.com/sso/oauth2.0/accessToken'

# the URL for niantic labs
URL_API = 'https://pgorelease.nianticlabs.com/plfe/rpc'

# global debug
DEBUG = False

class Settings(object):
    def __init__(self, box_num, host_ip, db_host, db_user, db_pass, db_name, users):
        # box settings
        self.box_num = int(box_num)
        self.host_ip = host_ip

        # users to access api servers
        self.users = users

        # MySQL creds
        self.db_host = db_host
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_name = db_name

        self.db_cxn = MySQLdb.connect(host=self.db_host, user=self.db_user, passwd=self.db_pass, db=self.db_name)

    def __str__(self):
        return 'box_num: ' + str(self.box_num) + ', host_ip: ' + str(self.host_ip) + ', db_host: ' + str(db_host) + ', db_user: ' + str(db_user) + ', db_pass: ' + str(db_pass) + ', db_name: ' + str(db_name)

    def close(self):
        '''
        Closes the DB connection
        '''
        try:
            self.db_cxn.close()
        except Exception as e:
            print ('Unable to close DB connection ' % e)


# read file for settings
json_data=open('./settings/settings.json').read()
data = json.loads(json_data)
s = data

# ip of this machine
host_ip = socket.gethostbyname(socket.gethostname())

# construct settings object
settings = Settings(s['general']['box_num'], host_ip, s['database-creds']['host'], s['database-creds']['user'], s['database-creds']['pass'], s['database-creds']['database'], s['users'])

def getSettings():
    '''
    Returns:
        The construct settings object.
    '''
    return settings

def getDatabase():
    '''
    Returns: 
        The database connection.
    '''
    try:
        return settings.db_cxn
    except Exception as e:
        print ('Unable to grab DB connection ' % e)