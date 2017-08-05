# Pokemon-Go-Locator-Server
This repository was designed to service a [client app](TODO), caching the results of the NianticAPI pull requests and storing them locally in the database. This would allow other users to see Pokemon outside of their scan radius, so they can target specific species.

## Requirements
- Python 2.7+
- [Flask](http://flask.pocoo.org)
- MySQL

All python modules and extensions under [requirements.txt](https://github.com/Unknowncmbk/Pokemon-Go-Locator-Server/blob/master/requirements.txt).

## Installation
Make sure all requirements above are met and installed on the local machine you want to run this module. 

Add all queries in [database-schema.txt](https://github.com/Unknowncmbk/Pokemon-Go-Locator-Server/blob/master/database-schema.txt) to initialize the database structure.

Please make sure to add the settings for MySQL in the [settings file](https://github.com/Unknowncmbk/Pokemon-Go-Locator-Server/blob/master/settings/settings.json).

## Setup
In order to add scalability, `nexus.py` can be ran on multiple screens with different user accounts listed in the [settings file](https://github.com/Unknowncmbk/Pokemon-Go-Locator-Server/blob/master/settings/settings.json).

Setup a screen session:
```
screen -S worker1
```
and simply invoke the nexus module:
```
python nexus.py -u user1 -p pass1
```

This worker will service as many requests as Niantic will allow, so more than one worker screen might have to be set up.

Workers will populate the database contents with their pull requests from Niantic, caching their results for all users to be able to access.
