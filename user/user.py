#!/usr/bin/python

# local imports
import loc
from session import session
from settings import settings
from ext_api import niantic_api

# python modules

class User(object):
	def __init__(self, username, password):
		self.username = username

		# create the session token for this user
		self.session_token = session.get_access_token(username, password)

		if self.session_token is not None:

			# generate the session url based off token
			self.session_url = niantic_api.get_request_url(self.session_token, settings.URL_API)

			if self.session_url is not None:

				# fetch profile information
				self.profile = niantic_api.get_profile(self.session_token, self.session_url, loc.Location(), None)

			else:
				print('RPC server is offline!')
		else:
			print('Wrong username/password!')

	def __str__(self):
		return 'Username: ' + str(self.username) + ', Token: ' + str(self.session_token[:25]) + ', Req_URL: ' + str(self.session_url)

	def is_valid(self):
		'''
		Get whether or not the created User is a valid Pokemon Trainer Club user.

		Returns:
			True if the user is a valid club user, False otherwise
		'''
		if self.profile is None or not self.profile.payload:
			print('Unable to grab profile for ' + str(self.username))
			return False

		return True

	def print_profile_info(self):
		'''
		Prints to the console the information for this User's profile.
		'''
		if self.is_valid():
			payload = self.profile.payload[0]
			profile = pokemon_pb2.ResponseEnvelop.ProfilePayload()
			profile.ParseFromString(payload)
			print('Username: {}'.format(profile.profile.username))

			creation_time = datetime.fromtimestamp(int(profile.profile.creation_time) / 1000)
			print('You are playing Pokemon Go since: {}'.format(
				creation_time.strftime('%Y-%m-%d %H:%M:%S'),
			))

			print('Team: {}'.format(profile.profile.team))
			print('poke_storage: {}'.format(profile.profile.poke_storage))
			print('item_storage: {}'.format(profile.profile.item_storage))