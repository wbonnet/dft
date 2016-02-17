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

class Repository
#					"url" : "http://ftp.fr.debian.org/debian/" ,
#					"suite" : "jessie" ,
#					"sections" : [
#						"main" ,
#						"contrib" ,
#						"non-free"

class Distribuion:
#			"name" : "Debian Jessie" ,
#			"architecture" : [
#				"amd64" ,
#				"i386" ,
#				"armel" ,
#				"armhf"

class Package:
#			{ "name" : "apt" } ,


class GroupOfPackage : 
#			"group-name" : "base" ,
#			"packages"	: [
#				{ "name" : "ethtool" } ,
#				{ "name" : "gawk" } ,


class Flavour:
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
#/			"name" : "Beagleboard Black" ,
#//			"architecture" : "armel" ,
#//			"group-of-packages" : [
#//				"raspberry-pi-2-support"
#//			]
#//			repository ?
#//			kernel ?

class ProductionTarget:
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
