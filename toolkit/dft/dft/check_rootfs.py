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

import logging, os, subprocess, tarfile, shutil, tempfile, distutils
from distutils import dir_util, file_util
from cli_command import CliCommand


#
#    Class CheckRootFS
#
class CheckRootFS(CliCommand): 
  """This class implements method needed to check the base OS content.

  The content of the rootfs can be checked for mising or forbidden 
  packages, files, directories and symlink. Attributes, versions and 
  content can also be checked
  """

  # -------------------------------------------------------------------------
  #
  # __init__
  #
  # -------------------------------------------------------------------------
  def __init__(self, dft, project):
    """Default constructor
    """

    # Initialize ancestor
    super().__init__(dft, project)

    # Initialize a dictionnary to hold the list of installed packages
    self.installed_packages = { }

    # By default thecheckis successfull since not rules were checked
    # This boolean will be set to False (meaning check failed) as soon as a
    # rule verificationwill fail
    self.is_check_successfull = False


  # -------------------------------------------------------------------------
  #
  # check_rootfs
  #
  # ------------------------------------------------------------------------- 
  def check_rootfs(self):
    """This method implement the business logic of generating the rootfs. It calls
    dedicated method for each step. The main steps are :

    . setting up configuration (mostly rules and path to the rootfs to check)
    . setup QEMU if needed
    . check for packages
    . check for files, dirctories and symlink
    . cleanup QEMU if needed
    """

    # Check if we are working with foreign arch, then ... 
    if self.use_qemu_static == True:
      # QEMU is used, and we have to install it into the target
      self.setup_qemu()

    #
    # Check the packages
    #
    if self.project.check_definition != None and "packages" in self.project.check_definition:
      logging.debug("Packages check is activated")
      self.check_packages()
    else:
      logging.info("Packages check generation is deactivated")

    #
    # Check the files
    #
    if self.project.check_definition != None and "files" in self.project.check_definition:
      logging.debug("Files check is activated")
      self.check_packages()
    else:
      logging.info("Files check generation is deactivated")

    # Remove QEMU if it has been isntalled. It has to be done in the end
    # since some cleanup tasks could need QEMU
    if self.use_qemu_static == True:
      self.cleanup_qemu()


    # Check the final status and return an error if necessary
    if self.is_check_successfull == False:
      print("At least one rule failed, the check is UNSUCCESSFULL")
      exit(1)
        
  # -------------------------------------------------------------------------
  #
  # check_packages
  #
  # -------------------------------------------------------------------------
  def check_packages(self):
    """This method is in charge of contolling the packages installed in the 
    rootfs according to the rules loaded from the configurtion file.

    Packages can have several status :
    . mandatory  =>  it MUST  be installed
    . allowed    =>  it CAN   be installed
    . forbidden  =>  it CAN'T be installed

    Version of packages can also be controlled. Available checks are :
    . min-version          => LOWER versions CAN'T be installed
    . max-version          => MORE RECENT versions CAN'T be installed
    . allowed-version      => If installed, version MUST be onne of the given
                              version in the list
    . blacklisted-version  => NONE of the given version CAN be installed
                              it is a list
    - allowed-arch         => The packages is allowed only on the given archs
    - blacklisted-arch     => The packages is blacklisted on the given archs
    """
    logging.info("starting to check installed packages")

    # Generate the dpkg command to retrieve the list of installed packages
    sudo_command  = "LANG=C sudo chroot " + self.project.rootfs_mountpoint + " dpkg -l | tail -n +6"
    pkglist = self.execute_command(sudo_command)

    # Iterate the output of the dpkg process and build the dictionnary of
    # all installed packages
    for binaryline in pkglist.splitlines():
      # Each fields is stored into a variable to easy manipulation and 
      # simplify code. First get the array of words converted to UTF-8
      line = binaryline.decode('utf-8').split()

      # Extract each fields
      pkg_status      = line[0]
      pkg_name        = line[1]
      pkg_version     = line[2]
      pkg_arch        = line[3]

      # Build a dictionnary, using package name as main key
      self.installed_packages[pkg_name] = { 'status': pkg_status , 'version': pkg_version , 'arch': pkg_arch }

    # Now iterate the list of rules to check against installed packages
    for rule in self.project.check_definition["packages"]["mandatory"]:
      self.check_package_rules(rule, mandatory=True)

    for rule in self.project.check_definition["packages"]["forbidden"]:
      self.check_package_rules(rule, forbidden=True)

    for rule in self.project.check_definition["packages"]["allowed"]:
      self.check_package_rules(rule, allowed=True)

# TODO traiter les paquet en rc ?

  # -------------------------------------------------------------------------
  #
  # check_package_rules
  #
  # -------------------------------------------------------------------------
  def check_package_rules(self, rule, mandatory = None, forbidden = None, allowed = None):
    """This method is in charge of contolling if the rules defined for a
    given package are verified or not. It uses the same constraint definitions
    and structure as in chck_packages pethod.
    """
  
    # First let's control that all keywords (key dictionnaires) are valid and know
    for keyword in rule:
      if keyword not in "name" "min-version" "max-version" "allowed-version" "blacklisted-version" "allowed-arch" "blacklisted-arch":
        logging.error("Unknow keyword " + keyword + " when parsing packages rules. Rule is ignored")

    # Check if mandatory package is missing
    if mandatory == True and rule["name"] not in self.installed_packages:
      logging.info("Missing mandatory package : " + rule["name"])
      self.is_check_successfull = False
      return

    # Check if mandatory package is missing
    if forbidden == True and rule["name"] in self.installed_packages:
      logging.info("Forbidden package is installed : " + rule["name"])
      self.is_check_successfull = False
      return

    # Check version if higher or equal than min version
    if "min-version" in rule:
      return_code = 0
      if rule["name"] in self.installed_packages: 
        # Generate the dpkg command to compare the versions
        dpkg_command  = "dpkg --compare-versions " + rule["min-version"]
        dpkg_command  += " lt " + self.installed_packages[rule["name"]]["version"] 
        
        # We have to protect the subprocess in a try except block since dpkg
        # will return 1 if the check is invalid
        try: 
          compare_result = subprocess.run(dpkg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                   shell=True, check=True, universal_newlines=False)
          return_code = compare_result.returncode

        # Catch the execution exception and set return_code to something else than zero
        except subprocess.CalledProcessError as e:
          return_code = 1

        # If the result is not ok, then output an info an go on checking next keyword
        if return_code > 0:
          logging.info("Version " + self.installed_packages[rule["name"]]["version"] + " of package is older than minimum allowed version " + rule["min-version"])
          self.is_check_successfull = False
        else:
          logging.debug("Version " + self.installed_packages[rule["name"]]["version"] + " of package is newer than minimum allowed version " + rule["min-version"])

    # Check version if lower or equal than max version
    if "max-version" in rule:
      return_code = 0
      if rule["name"] in self.installed_packages: 
        # Generate the dpkg command to compare the versions
        dpkg_command  = "dpkg --compare-versions " + rule["max-version"]
        dpkg_command  += " gt " + self.installed_packages[rule["name"]]["version"]
        
        # We have to protect the subprocess in a try except block since dpkg
        # will return 1 if the check is invalid
        try: 
          compare_result = subprocess.run(dpkg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                   shell=True, check=True, universal_newlines=False)
          return_code = compare_result.returncode

        # Catch the execution exception and set return_code to something else than zero
        except subprocess.CalledProcessError as e:
          return_code = 1

        # If the result is not ok, then output an info an go on checking next keyword
        if return_code > 0:
          logging.info("Version " + self.installed_packages[rule["name"]]["version"] + " of package is newer than minimum allowed version " + rule["max-version"])
          self.is_check_successfull = False
        else:
          logging.debug("Version " + self.installed_packages[rule["name"]]["version"] + " of package is older than minimum allowed version " + rule["max-version"])

    # Check that version is in the list of allowed-version
    if "allowed-version" in rule:
      if rule["name"] in self.installed_packages: 
        if self.installed_packages[rule["name"]]["version"] not in rule["allowed-version"]: 
          logging.info("Version " + self.installed_packages[rule["name"]]["version"] + " of package " + rule["name"] + " is not allowed")
          self.is_check_successfull = False
        else:
          logging.debug("Version " + self.installed_packages[rule["name"]]["version"] + " of package " + rule["name"] + " is allowed")

    # Check that version is not in the list of blacklisted versions
    if "blacklisted-version" in rule:
      if rule["name"] in self.installed_packages: 
        if self.installed_packages[rule["name"]]["version"] in rule["blacklisted-arch"]: 
          logging.info("Version " + self.installed_packages[rule["name"]]["version"] + " of package " + rule["name"] + " is blacklisted")
          self.is_check_successfull = False
        else:
          logging.debug("Version " + self.installed_packages[rule["name"]]["version"] + " of package " + rule["name"] + " is allowed")

    # Check that architecture is not in the list of blacklisted arch
    if "blacklisted-arch" in rule:
      if rule["name"] in self.installed_packages: 
        if self.installed_packages[rule["name"]]["arch"] in rule["blacklisted-arch"]: 
          logging.info("Package " + rule["name"] + " is blacklisted on architecture " + self.installed_packages[rule["name"]]["arch"])
          self.is_check_successfull = False
        else:
          logging.debug("Package " + rule["name"] + " is not blacklisted on architecture " + self.installed_packages[rule["name"]]["arch"])

    # Check that version is in the list of allowed arch
    if "allowed-arch" in rule:
      if rule["name"] in self.installed_packages: 
        if self.installed_packages[rule["name"]]["arch"] not in rule["allowed-arch"]: 
          logging.info("Package " + rule["name"] + " is not allowed for architecture " + self.installed_packages[rule["name"]]["arch"])
          self.is_check_successfull = False
        else:
          logging.debug("Package " + rule["name"] + " is allowed for architecture " + self.installed_packages[rule["name"]]["arch"])



  # -------------------------------------------------------------------------
  #
  # check_files
  #
  # -------------------------------------------------------------------------
  def check_files(self):
    """This method is in charge of contolling the files (and also 
    directories and symlinks) installed in the rootfs according to the 
    rules loaded from the configurtion file.

    Files ia a term that identify any object in the file system. A 'file'
    can be a standard file, but also a directory or a symlink (special 
    devices are not handled, yet...). As a standard file, a package is a 
    file. 

    Checks on packages from what the check_packages method does. This 
    method wil lookfor the foo.deb file in itself, not if it is installed
    what is its versions etc. 

    Files can have several status :
    . mandatory  =>  it MUST  be installed
    . allowed    =>  it CAN   be installed
    . forbidden  =>  it CAN'T be installed

    A file is defined by it path. The following attributes can be checked :
    . type           file, directory or symlink. Default is file
    . owner          since owner and group can be either numric or text,   
    . group          it has to be checked inside the chrooted environment
    . mask
    . target         only if type is symlink
    . empty          only for files and directories (zero sized for file, 
                     and no centent at all for directories)
    . md5            file (or symlink target) checksum computed with MD5
    . sha1           file (or symlink target) checksum computed with SHA1
    . sha256         file (or symlink target) checksum computed with SHA256

    """
# TODO controler le sha dans les tests unitaires

    # Iterate the list of rules to check against installed packages
    # Files will be checked on an individual basis, which is different of
    # packages. Package list can be retrieved with a single call to dpkg.
    # Retrieving the complete file list would cost too much
    for rule in self.project.check_definition["packages"]["mandatory"]:
      self.check_file_rules(rule, mandatory=True)

    for rule in self.project.check_definition["packages"]["forbidden"]:
      self.check_file_rules(rule, forbidden=True)

    for rule in self.project.check_definition["packages"]["allowed"]:
      self.check_file_rules(rule, allowed=True)

    logging.info("starting to check installed packages")
