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
# Copyright 2016 DFT project (http://www.debianfirmwaretoolkit.org).  
# All rights reserved. Use is subject to license terms.
#
# Debian Firmware Toolkit is the new name of Linux Firmware From Scratch
# Copyright 2014 LFFS project (http://www.linuxfirmwarefromscratch.org).  
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

import argparse, textwrap
import build_baseos

#
#	Class Cli
#
class Cli:
	"""This class represent the command line parser for this tool. It brings 
	methods used to parse command line arguments then run the program itself
	"""

	def __init__(self):
		# Current version
		self.version = "0.0.2"

		# Create the internal parser from argparse
		self.parser = argparse.ArgumentParser(description=textwrap.dedent('''\
Debian Firmware Toolkit v''' + self.version + ''' - DFT is a collection of tools used to create Debian based firmwares 
					 			 
Available commands are :
. assemble_firmware                Create a firmware from a baseos and generate the configuration files used to loading after booting
. build_baseos                     Generate a debootstrap from a Debian repository, install and configure required packages
. build_bootloader                 Build the bootloader toolchain (kernel, initramfs, grub or uboot)
. build_image                      Build the disk image from the firmware (or rootfs) and bootloader toolchain
. build_firmware                   Build the firmware configuration files and scripts used to load in memory the firmware
. check_rootfs                     Control the content of the baseos rootfs after its generation (debsecan and openscap)
. factory_setup                    Apply some extra factory setup before generating the firmware
. generate_content_information     Generate a manifest identiyfing content and versions
. strip_rootfs                     Strip down the rootfs before assembling the firmware'''),
											  formatter_class=argparse.RawTextHelpFormatter)
	
	def parse(self, args):
		# Stores the argument in the instance
		self.command = args

		self.add_parser_option_common()
		
		# According to the command, call the method dedicated to parse the arguments
		if   self.command == "assemble_firmware":            self.add_parser_option_assemble_firmware()
		elif self.command == "build_baseos":                 self.add_parser_option_build_baseos()
		elif self.command == "build_bootloader":             self.add_parser_option_build_bootloader()
		elif self.command == "build_image":                  self.add_parser_option_build_image()
		elif self.command == "build_firmware":               self.add_parser_option_build_firmware()
		elif self.command == "check_rootfs":                 self.add_parser_option_check_rootfs()
		elif self.command == "factory_setup":                self.add_parser_option_factory_setup()
		elif self.command == "generate_content_information": self.add_parser_option_generate_content_information()
		elif self.command == "strip_rootfs":                 self.add_parser_option_strip_rootfs()
		else:							                     
			# If the command word is unknown, the force the parsing of the help flag
			return self.parser.parse_args(['-h']) 

		# Finally call the parser that has been completed by the previous lines
		self.parser.parse_args() 

	def add_parser_option_assemble_firmware(self):
		pass

	def add_parser_option_build_baseos(self):
		# Add the arguments
		self.parser.add_argument(	'build_baseos', 
								 	help='Command to execute')

		# Configuration file store the definition of baseos. Optioncan be 
		# overriden by arguments on the command line (like --target-arch)
		#
		# Configuration file defines baseos and its modulation
		self.parser.add_argument(	'--config-file',
									action='store',
                      				dest='config_file',
                      				required=True,
									help='baseos configuration file')	

		# Project definition file defines environnement shared between
		# the different DFT commands (such as path to diirectory storing)
		# cache archives, temporary working dir, temp dir name patterns, etc.)
		self.parser.add_argument(	'--project-file',
									action='store',
                      				dest='project_file',
									help='project definition file')	

		# Overrides the target architecture from the configuration file by
		# limiting it to a given list of arch. Architectures not defined in 
		# the configuration file can be added with this parameter
		# TODO: parse the list of argument. So far only one value is handled
		self.parser.add_argument(	'--limit-arch',
									action='store',
                      				dest='limit_target_arch',
									help='limit the list of target arch to process (comma separated list of arch eg: arch1,arch2)')	

		# Overrides the target version used to build the baseos. Version to 
		# use is limited it to a given list of arch. Versions not defined
		# in the configuration file can be added with this parameter
		# TODO: parse the list of argument. So far only one value is handled
		self.parser.add_argument(	'--limit-version',
									action='store',
                      				dest='limit_target_version',
									help='limit the list of target version to process (comma separated list of versions eg: jessie,stretch)')	

		# Activate the use of the rootfs cache archive. When building a baseos
		# with debootstrap, having this option enable will make DFT look for
		# an existing cache archive, an extract it instead of doing a fresh 
		# debootstrap installation
		self.parser.add_argument(	'--use-cache-archive',
									action='store_true',
                      				dest='use_cache_archive',
									help="activate the use of an existing cache archive (extract archive instead of running debootstrap). \n"
									 	 "This option does nothing if the cache archive do no exist. In this case, debootstrap will be \n"
										 "launched and the missing archive will not be created")

		# Activate the use of the rootfs cache archive. When building a baseos
		# with debootstrap, having this option enable will make DFT look for
		# an existing cache archive, an extract it instead of doing a fresh 
		# debootstrap installation
		self.parser.add_argument(	'--update-cache-archive',
									action='store_true',
                      				dest='update_cache_archive',
									help="update the cache archive after building a baseos with debootstrap. Existing archive will\n"
										 "be deleted if it already exist, or it will be created if missing")

		# Override the list of mirrors defined in the configuration file. 
		# This option defines a single mirror, not a full list of mirrors.
		# Thus the list of mirrors will be replaced by a single one 
		self.parser.add_argument(	'--override-debian-mirror',
									action='store',
                      				dest='override_debian_mirror',
									help="override the list of mirrors defined in the configuration file. This option \n"
										 "defines a single mirror, not a full list of mirrors. Thus the list of mirrors \n"
										 "will be replaced by a single one")
		
		# delete work dir
		# => should not be in this command ? move it to buil_firmware ?

		# deactivate systemd ? 
		# => not really sure about this...

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

	def add_parser_option_common(self):
		# Activate the use of the rootfs cache archive. When building a baseos
		# with debootstrap, having this option enable will make DFT look for
		# an existing cache archive, an extract it instead of doing a fresh 
		# debootstrap installation
		self.parser.add_argument(	'--log-level',
									action='store',
                      				dest='log_level',
                                    choices=['debug', 'info', 'warning', 'error', 'critical'],
									help="defines the minimal log level. Default value is  warning")


	def run(self):
		""" According to the command, call the method dedicated to run the
			command called from cli
		"""
		# 
		if   self.command == "assemble_firmware":            self.run_assemble_firmware()
		elif self.command == "build_baseos":                 self.run_build_baseos()
		elif self.command == "build_bootloader":             self.run_build_bootloader()
		elif self.command == "build_image":                  self.run_build_image()
		elif self.command == "build_firmware":               self.run_build_firmware()
		elif self.command == "check_rootfs":                 self.run_check_rootfs()
		elif self.command == "factory_setup":                self.run_factory_setup()
		elif self.command == "generate_content_information": self.run_generate_content_information()
		elif self.command == "strip_rootfs":                 self.run_strip_rootfs()
	
	def run_assemble_firmware(self):
		pass

	def run_build_baseos(self):
		""" Method used to handl eth build_baseos command. 
			Create the business objet, then execute the entry point
		"""
		# Create the business object
		command = build_baseos.BuildBaseOS()

		# Then
		command.install_baseos()
		pass

	def run_build_bootloader(self):
		pass

	def run_build_image(self):
		pass

	def run_build_firmware(self):
		pass

	def run_check_rootfs(self):
		pass

	def run_factory_setup(self):
		pass

	def run_content_information(self):
		pass

	def run_strip_rootfs(self):
		pass