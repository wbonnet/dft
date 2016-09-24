#
# The contents of this file are subject to the Apache 2.0 license you may not
# use this file except in compliance with the License.
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
#
# Copyright 2014 LFFS project (http://www.linuxfirmwarefromscratch.org).  
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet 	wllmbnnt@gmail.com
#
#
import argparse

#
#	Class Cli
#
class Cli:
	"""This class represent the command line parser for this tool. It brings 
	methods used to parse command line arguments then run the program itself
	"""

	def __init__(self):
		"""Default constructor. Initialize the 
    	"""    	
		
		# Create the internal parser from argparse
		self.parser = argparse.ArgumentParser(description='LFFS - Build a RootFS using given json description file.')

		# Add the arguments
		self.parser.add_argument('integers', metavar='N', type=int, nargs='+', help='an integer for the accumulator')

		# help
		# version
		# file json
		# production target list comma separated
		# use cache
		# update cache
		# proxy ?
		# update cache
		# activation de systemd ?
		# qemu static
		# cache dir
		# prod dir
		# project file ?   json qui contiendrait les infos nécessaires plutot que de tout passer en option. Ce sera utile pour les autres

		
#parser.add_argument('--sum', dest='accumulate', action='store_const',
#                    const=sum, default=max,
#                    help='sum the integers (default: find the max)')

#args = parser.parse_args()
#print(args.accumulate(args.integers))
		pass

	def parse(self, args):
		"""Command line parser. Initiliaze the internal structure and check 
		arguments before running the tool
		
    	Args:
			args : arguments received in sys.argv from the command line
    	"""
#		self. = 
		print("plop")
		pass

	def run(self):
		pass