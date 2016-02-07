#!/usr/bin/python2
# -*- coding: utf-8 -*-

#
#  The contents of this file are subject to the GNU General Public License 
#  Version 3 or later (the "GPL") you may not use this file except in 
#  compliance with the License.
# 
#  Software distributed under the License is distributed on an "AS IS" basis,
#  WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
#  for the specific language governing rights and limitations under the
#  License.
# 
#  This work is derivated work based upon mGAR build system from OpenCSW 
#  project (http://www.opencsw.org).
#
#  Copyright 2001 Nick Moffitt: GAR ports system
#  Copyright 2006 Cory Omand: Scripts and add-on make modules, except where otherwise noted.
#  Copyright 2008 Dagobert Michelsen (OpenCSW): Enhancements to the CSW GAR system
#  Copyright 2008-2013 Open Community Software Association: Packaging content
#
#  Copyright 2013 LINAGORA (http://www.linagora.com).  All rights reserved.
#  Use is subject to license terms.
#
#  Contributors list :
#
#    William Bonnet         wbonnet@linagora.com
#


# Standard import
import sys, os

# Run shell commands
import subprocess


# 
# -----------------------------------------------------------------------------
#
class PackageUtility():
    '''
        This is is the base class for the package utility tool. It provides the
        basic functions to check if a package is installed, or to install it
    '''

    def __init__(self):
        '''
            Default constructor, it only retrieves the distribution flavor
        '''

        # Retrieve the distribution name using lsb_release tool
        p      = subprocess.Popen(["lsb_release", "-i"], stdout=subprocess.PIPE)
        self.distro = p.communicate()[0].split()[-1].lower()


    def check(self, package_list):
        '''
        Check if the given list of packages is installed
        '''
        
        # Some verbosity
        print "    checking dependencies installation"
        
        # Initialize the return code, so far no missing package
        status = 0

        # Iterate the list of package. Index 0 contains the name of this
        # script, index 1 the command word
        for package in package_list[2:]:
            if self.distro == "ubuntu" or self.distro == "debian":
                is_installed = self.check_if_package_is_installed_on_debian_based_system(package)
            else:
                print("        unknown distribution : ", self.distro)
                return 1

            if is_installed == True:    
                print "        [  OK   ] : ", package
            else: 
                print "        \x1b[1m[Missing] : ", package, "\x1b[0m"
                status = 1

        # Return 1 if a package is missing
        return status

    def install(self, package_list):
        '''
        Check if the given list of packages is installed and install missing
        packages.
        '''

        # Some verbosity
        print "    installing missing dependencies"

        # Initialize the return code, so far no missing package
        status = 0

        # Iterate the list of package. Index 0 contains the name of this
        # script, index 1 the command word
        for package in package_list[2:]:
            if self.distro == "ubuntu" or self.distro == "debian":
                is_installed = self.check_if_package_is_installed_on_debian_based_system(package)
            else:
                print("        unknown distribution : ", distro)
                return 1

            if is_installed == True:    
                print "        [    OK    ] : ", package
            else:
                print "        \x1b[1m[Installing] : ", package, "\x1b[0m. This can take some time..."
                if self.install_package_on_debian_based_system(package) == False:
                    status = 1

        # Return 1 if a package is missing
        return status

    def install_package_on_debian_based_system(self, package):
        '''
        Install a package on ubuntu, debian, ... systems
        '''

        # Call apt-get to install the package
        p      = subprocess.Popen(["sudo", "apt-get", "-y", "install",  package], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
        (result, err) = p.communicate()
        if len (err) > 0:
	        print "        Unable to install", package
	        print err
	        return 5

        print result        
        if len(result) > 0:
            return True
        else:
            return False

    def check_if_package_is_installed_on_debian_based_system(self, package):
        '''
        Check if a package is installed on ubuntu, debian, ... systems
        '''

        # Call dpkg-query to check if it is installed
        p      = subprocess.Popen(["dpkg-query", "-W", package], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
        result = p.communicate()[0].split()
        if len(result) > 1:
            return True
        else:
            return False

# 
# -----------------------------------------------------------------------------
#
def main(argv=None):
    '''
    Check for the operating system, then parse the command line and call the 
    install checker for each package
    '''

    # Get the arguments
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

     # Create the command line helper
    cli = PackageUtility()

    # Return code, 0 means everything fine
    status = 0

    # Check that there is at least 2 args
    if len(argv) < 2:
        print "    Too few arguments to call package_utility (", len(argv), " should be at least 2 )"
        return 3
        
    # Call the method associated to the argument
    if argv[1] == "check":
    	status = cli.check(argv)
    elif argv[1] == "install":
    	status = cli.install(argv)
    else:
        print "    Unknown command word (", argv[1], " )"
        return 4

    # Return 1 if a package is missing
    return status
 
# ---------------------------------------------------------------------------------------------------------------------
# Simple test to return result of main method

if __name__ == "__main__":
    sys.exit(main())                        
