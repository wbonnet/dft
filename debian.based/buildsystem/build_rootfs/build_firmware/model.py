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

class Repository:
	"""This class contains Debian repository informations.

	   Repository are Distribution components. Each distribution contains one or more repository
	"""

	def __init__(self, url, suite, sections):
		"""Default constructor
		
    	Args:
			url		 	(str) 		: URL of the repository (eg: http://security.debian.org/debian/)
			suite		(str) 		: Repository suite, typically the version (eg: jessie/updates or jessie)
			sections	(str array) : List of sections used from this repo (eg: ["main", "contrib", "non-free"])

    	"""
		self.url = url
		self.suite = suite
		self.sections = sections

class Distribuion:
	"""This class contains the definition of a Debian distribution. 

	   A distribution is defined by its name, the list of supported architecture and the list of available repositories
	"""

	def __init__(self, name, architectures, repositories):
		"""Default constructor
		
    	Args:
			name			(str)	 		: Name of the distribution (eg: Debian Jessie)
			architectures	(str array)		: Array containing the name of each architecture we use (eg: ["amd64", "armel"])
			repositories	(object array) 	: List of sections used from this repo (eg: ["main", "contrib", "non-free"] )

    	"""
		self.name = name
		self.architectures = architectures
		self.repositories = repositories

class Package:
	"""This class contains the definition of a package

	   In this version it is only defined by its name. Future evolution may include version management.
	"""

	def __init__(self, name):
		"""Default constructor
		
    	Args:
			name			(str)	 		: Name of the package (eg: htop bash or less)

    	"""
		self.name = name

class GroupOfPackage : 
	"""This class for groups of packages

	   Groups of packages are provided for convinience and packages manipulation. 
	"""

	def __init__(self, group_name):
		"""Default constructor
		
    	Args:
			name		(str)		: Name of the group of packages (eg: "Beagle Bone black BSP" or "Security tools")
			packages   	(str array) : Array containing all the packages name included in this group

    	"""
		self.group_name = group_name
		self.packages = packages

class Flavour:
	"""This class defines flavours

	   Flavours are used to create modulation on rootfs and firmware. A firmware will be generated
	   in different version, one for each associated flavour. Each flavour defines lists of packages
	   to add or to exclude to create the variation.
	"""

	def __init__(self, name, group_of_packages, exclude_group_of_packages, packages):
		"""Default constructor
		
    	Args:
			name						(str)			: Name of the flavour (eg: "Debug" or "Validation")
			packages  					(object array) 	: Array containing all the packages to include in this flavour
			group_of_packages  			(object array) 	: Array containing all the group of packages to include in this flavour
			exclude_group_of_packages	(object array) 	: Array containing all the group of packages to exclude from this flavour

    	"""
		self.name = name
		self.group_of_packages = group_of_packages
		self.exclude_group_of_packages = exclude_group_of_packages
		self.packages = packages

class Firmware:
	"""This class defines a firmware

	   A firmware is a distribution installed from a list of packages. They are defined by
	   a list of group of packages and a completary list of packages to install. Optionnaly 
	   a firmware can also be based on another on. In this case it will be used as ancestor	   
	"""

	def __init__(self, name, group_of_packages, packages, based_on_firmware):
		"""Default constructor
		
    	Args:
			name				(str)			: Name of the firmware (eg: "fw-rpi3")
			packages  			(object array) 	: Array containing all the packages to include in this firmware
			group_of_packages  	(object array) 	: Array containing all the group of packages to include in this firmware
			based_on_firmware	(object)	 	: Firmware to use as 'parent'

    	"""
		self.name = name
		self.group_of_packages = group_of_packages
		self.packages = packages
		self.based_on_firmware = based_on_firmware

class Board:
	"""This class defines a board

	A board is the physical target for which the firmware is generated. It is defined by its name, architecture 
	and a list of package (which should be used for BSP)
	"""

	def __init__(self, name, architecture, group_of_packages):
		"""Default constructor
		
    	Args:
			name				(str)			: Name of the group of packages (eg: "Beagle Bone black BSP" or "Security tools")
			architecture		(str)		 	: Architecture of the board (eg: armhf, arm64)
			group_of_packages  	(object array) 	: Array containing all the group of packages to include in this firmware

    	"""
		self.name = name
		self.architecture = architecture
		self.group_of_packages = group_of_packages

class ProductionTarget:
	"""Definition of production targets

	Production targets contains all the information mandotory to create the binary firmware.
	These information are defined in a tuple including the target board, the distributionto use
	the firmware, and some flavours to build
	"""

	def __init__(self, name, include_in_build, board, distribution, firmware, flavours):
		"""Default constructor
		
    	Args:
			name				(str)			: Name of the production target (eg: "test-Jessie-rpi2")
			include-in-build	(boolean)		: Is the target included in the production
			board 				(object)		: Board to use for this production target
			distribution        (object)		: Distribution to use for this production target
			firmware  			(object)		: Firmware to use for this production target
			flavours-to-build"  (object array)  : Flaours to generate for this production target

    	"""
		self.name = name
		self.include_in_build = include_in_build
		self.board = board
		self.distribution = distribution
		self.firmware = firmware
		self.flavours = flavours