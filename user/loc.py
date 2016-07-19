#!/usr/bin/python

# local imports
from session import session
from settings import settings

# python modules
import struct
from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

def f2i(float):
	return struct.unpack('<Q', struct.pack('<d', float))[0]

def f2h(float):
	return hex(struct.unpack('<Q', struct.pack('<d', float))[0])

def h2f(hex):
	return struct.unpack('<d', struct.pack('<Q', int(hex, 16)))[0]

class Location(object):
	def __init__(self):

		# the default starting lat/lng
		self.default_lat = 0
		self.default_lng = 0

		# the current representation of lat/lng
		self.float_lat = 0
		self.float_lng = 0

		# coordinates for latitude, longitude, altitude
		self.coords_lat = 0
		self.coords_lng = 0
		self.coords_alt = 0

	def get_loc_coords(self):
		'''
		Returns:
			The location coordinates in the form of (latitude, longitude, altitude).
		'''
		return (self.coords_lat, self.coords_lng, self.coords_alt)

	def set_loc_coords(self, lat, lng, alt):
		'''
		Sets this object's location coords to the specified values.

		Args:
			lat: The new latitude
			lng: The new longitude
			alt: The new altitude
		'''
		self.float_lat = lat
		self.float_lng = lng
		self.coords_lat = f2i(lat)
		self.coords_lng = f2i(lng)
		self.coords_alt = f2i(alt)

	def determine_location(self, location_name):
		'''
		Attempt to get the coordinates from Google Location until we have them.

		Args:
			location_name: The name of the location to pass to the API

		Returns:
			False if we are unable to get the coordinates for the specified location.
			True if we determine the coordinates, populating this Location.
		'''
		tries = 10

		while tries > 0:
			try:

				# grab geolocator
				geolocator = GoogleV3()
				loc = geolocator.geocode(location_name)

				print('[!] Your given location: {}'.format(loc.address.encode('utf-8')))
				print('[!] lat/long/alt: {} {} {}'.format(loc.latitude, loc.longitude, loc.altitude))
				global deflat
				global deflng

				self.default_lat = loc.latitude
				self.default_lng = loc.longitude
				self.set_loc_coords(loc.latitude, loc.longitude, loc.altitude)

				return True
			except (GeocoderTimedOut, GeocoderServiceError) as e:
				print('An error occurred while decoding location!')
				print(str(e))
				time.sleep(1.25)

			tries = tries - 1

		return False