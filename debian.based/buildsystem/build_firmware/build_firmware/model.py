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
	'Class for reposotories'

	def __init__(self, url, suite, sections):
		self.url = url
		self.suite = suite
		self.sections = sections
#					"url" : "http://ftp.fr.debian.org/debian/" ,
#					"suite" : "jessie" ,
#					"sections" : [
#						"main" ,
#						"contrib" ,
#						"non-free"

class Distribuion:
	'Class for distributions'

	def __init__(self, name, architecture):
		self.name = name
		self.architecture = architecture
#			"name" : "Debian Jessie" ,
#			"architecture" : [
#				"amd64" ,
#				"i386" ,
#				"armel" ,
#				"armhf"

class Package:
	'Class for packages'

	def __init__(self, name):
		self.name = name
#			{ "name" : "apt" } ,


class GroupOfPackage : 
	'Class for groups of packages'

	def __init__(self, group_name):
		self.group_name = group_name
		self.packages = packages
#			"group-name" : "base" ,
#			"packages"	: [
#				{ "name" : "ethtool" } ,
#				{ "name" : "gawk" } ,


class Flavour:
	'Class for flavours'

	def __init__(self, name, exclude_group_of_packages, packages):
		self.name = name
		self.exclude_group_of_packages = exclude_group_of_packages
		self.packages = packages
#			"name" : "debug",
#			"group-of-packages" : [
#				"debug"
#			], 
#			"exclude-group-of-packages" : [
#				"security"
#			] 
#			"packages" : [
#				"iotop" 
#			]


class Firmware:
	'Class for firmwares'

	def __init__(self, name, group_of_packages, packages, based_on_firmware):
		self.name = name
		self.group_of_packages = group_of_packages
		self.packages = packages
		self.based_on_firmware = based_on_firmware
#			"name" : "test",
#			"group-of-packages" : [
#				"base" ,
#				"security"
#			] ,
#			"packages" : [
#				"less" 
#			]
#		},
#""		{
#			"name" : "depends-test",
#			"based-on-firmware" : [
#				"test"
#			] ,
#			"packages" : [
#				"iotop" 
#			]
#		}

class Board:
	'Class for boards'

	def __init__(self, name, architecture, group_of_packages):
		self.name = name
		self.architecture = architecture
		self.group_of_packages = group_of_packages
#/			"name" : "Beagleboard Black" ,
#//			"architecture" : "armel" ,
#//			"group-of-packages" : [
#//				"raspberry-pi-2-support"
#//			]
#//			repository ?
#//			kernel ?

class ProductionTarget:
		'Class for production targets'

#			"include-in-build" : false , 
#""			"name" : "test-Jessie-rpi2" ,
#			"board" : "Raspberry PI 2" ,
#			"distribution" : "Debian Jessie" ,
#			"firmware" : "test" ,
#			"flavours-to-build" : [
#				"production" ,
#				"validation" ,
#				"debug"
#			]
