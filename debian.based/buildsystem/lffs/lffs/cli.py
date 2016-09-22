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
#    William Bonnet     wllmbnnt@gmail.com
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
		# Current version
		self.version = "0.0.1"

		# Create the internal parser from argparse
		self.parser = argparse.ArgumentParser(description='Linux Firmware From Scratch v' + self.version + '. LFFS is a collection of tools used to create Linux based firmwares')
	
	def parse(self, args):
		# According to the command, call the method dedicated to parse the arguments
		if   args == "assemble_firmware":            self.add_parser_option_assemble_firmware()
		elif args == "build_baseos":                 self.add_parser_option_build_baseos()
		elif args == "build_bootloader":             self.add_parser_option_build_bootloader()
		elif args == "build_image":                  self.add_parser_option_build_image()
		elif args == "build_firmware":               self.add_parser_option_build_firmware()
		elif args == "check_rootfs":                 self.add_parser_option_check_rootfs()
		elif args == "factory_setup":                self.add_parser_option_factory_setup()
		elif args == "generate_content_information": self.add_parser_option_generate_content_information()
		elif args == "strip_rootfs":                 self.add_parser_option_strip_rootfs()
		else:                                        self.add_parser_option_unknown()
		self.parser.parse_args() 

	def add_parser_option_assemble_firmware(self):
		pass

	def add_parser_option_build_baseos(self):
		# Add the arguments
		self.parser.add_argument(	'build_baseos', 
								 	help='Command to execute')
		
		self.parser.add_argument(	'-c',
                      				'--config-file',
									action='store',
                      				dest='config_file',
                      				required=True,
									help='baseos configuration file')	

		self.parser.add_argument(	'-p',
									action='store',
                      				dest='project_file',
									help='project definition file')	
		# Rescrit target arch ? 
		# Use cache do not rebuild
		# Configuration file
		# override mirror ?
		# delete work dir
		# override debian version ?
		# update cache file ? 
		# project configuration file ?
		# Use qemu ?
		# deactivate systemd ? 

	def add_parser_option_build_bootloader(self):
		pass

	def add_parser_option_build_image(self):
		pass

	def add_parser_option_build_firmware(self):
		#	Generate squashfs file
		pass

	def add_parser_option_check_rootfs(self):
		pass

	def add_parser_option_factory_setup(self):
		pass

	def add_parser_option_generate_content_information(self):
		pass

	def add_parser_option_strip_rootfs(self):
		pass

	def add_parser_option_unknown(self):
		# Add the arguments
		self.parser.add_argument('command', help='Command to execute')

	def run(self):
		pass