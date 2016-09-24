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

class DftConfiguration : 
	"""This class defines configuration for the DFT toolchain

       The tool configuration contains environment variables used to define 
       information such as default root working path, cache directories, etc.
	"""

	def __init__(self, group_name):
		"""Default constructor
		
    	Args:
#			name		(str)		: Name of the group of packages (eg: "Beagle Bone black BSP" or "Security tools")
#			packages   	(str array) : Array containing all the packages name included in this group

    	"""
il faut
le nom du fichier de config par defaut
le nom du fichier de config a utiliser
le repertoire de travail racine par defaut  il faut voir l interet ?
le repertoire de cache ?

		self.group_name = group_name
		self.packages = packages

class ProjectConfiguration :
    """This class defines projet configuration

       The project configuration contains environment variables used to define
       information such as working path, production targets to build
    """ 

    def __init__(self, group_name):
        """Default constructor

        Args:
#           name        (str)       : Name of the group of packages (eg: "Beagle Bone black BSP" or "Security tools")
#           packages    (str array) : Array containing all the packages name included in this group

        """
il faut
le nom du fichier de config par defaut
le nom du fichier de config a utiliser
la liste des prod targets a faire
le repertoire de travail
le repertoire de cache ?

        self.group_name = group_name
        self.packages = packages


il faut creer les obkets pour la config de l'outil et pour la config d'un projet

