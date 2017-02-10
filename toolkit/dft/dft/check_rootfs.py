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

import logging, os, subprocess, tarfile, shutil, tempfile, distutils, hashlib
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

    # By default the check is successfull since not rules were checked
    # This boolean will be set to False (meaning check failed) as soon as a
    # rule verification will fail
    self.is_check_successfull = True
    
    # This variable is used to store the result of a single rule check
    # The variable value is reset for each loop, while the scope of the 
    # previous one is the whole execution
    self.is_rule_check_successfull = True
    self.is_rule_check_successfull = True

    # Size of block used to read files whencomputing hashes
    self.block_size = 65536

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
      self.check_files()
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
    . allowed-version      => If installed, version MUST be one of the given
                              version in the list
    . blacklisted-version  => NONE of the given version CAN be installed
                              it is a list
    - allowed-arch         => The packages is allowed only on the given archs
    - blacklisted-arch     => The packages is blacklisted on the given archs
    """

    # Rule counter used to display the total number of checked rules
    rule_counter = 0
    
    # Counter used to display the number of successful rules
    rule_successfull_counter = 0

    # Counter used to display the number of failed rules
    rule_failed_counter = 0

    # Counter used to display the number of rules matching expected result
    # either failed of successfull, but as expected (handy for unit tests)
    rule_as_expected_counter = 0

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

    #
    # Now iterate the list of rules to check against installed packages
    # Process the "mandatory" rules group
    #
    for rule in self.project.check_definition["packages"]["mandatory"]:
      # Rule counter used to display the total number of checked rules
      rule_counter += 1

      # Call the check package method
      self.check_package_rules(rule, mandatory=True)

      # If the test was negative, then change the global result to false
      if self.is_rule_check_successfull == False:
        # Set the global failure flag
        self.is_check_successfull = False
        # Counter used to display the number of failed rules
        rule_failed_counter += 1
      else:
        # Counter used to display the number of successful rules
        rule_successfull_counter += 1
        
      # If the expected result variable has been defined, the compare it value
      # to the actual method result, and output a critical if different
      # expected-result value is used in unit testing context, and it should 
      # never be different unless something nasty is lurking inthe dark
      if "expected-result" in rule:
        if rule["expected-result"] != self.is_rule_check_successfull:
          logging.critical("-----------------------------------------------------------------------------")
          logging.critical("Unit test failed ! Expected result was " + str(rule["expected-result"]) + " and we got " + str(self.is_rule_check_successfull))
          print(rule)
          logging.critical("-----------------------------------------------------------------------------")
        else: 
          # Counter used to display the number of rules matching expected result
          # either failed of successfull, but as expected (handy for unit tests)
          rule_as_expected_counter += 1

      # Test if the label field is defined, if yes we have to output a message
      # for this rule with the result of the check
      if "label" in rule:
        # Define an empty result
        label_check_result = ""
        # If the check is successful, set the label to OK
        if self.is_rule_check_successfull == False:
          label_check_result = "[ OK ]"
        else:
          # Otherwise set it to fail
          label_check_result = "[FAIL]"
        # And print the test number, label and result to stdout
        print(label_check_result + " " + rule["label"])

    #
    # Process the "forbidden" rules group
    #
    for rule in self.project.check_definition["packages"]["forbidden"]:
      # Rule counter used to display the total number of checked rules
      rule_counter += 1

      # Call the check package method
      self.check_package_rules(rule, forbidden=True)

      # If the test was negative, then change the global result to false
      if self.is_rule_check_successfull == False:
         # Set the global failure flag
        self.is_check_successfull = False
        # Counter used to display the number of failed rules
        rule_failed_counter += 1
      else:
        # Counter used to display the number of successful rules
        rule_successfull_counter += 1

      # If the expected result variable has been defined, the compare it value
      # to the actual method result, and output a critical if different
      # expected-result value is used in unit testing context, and it should 
      # never be different unless something nasty is lurking inthe dark
      if "expected-result" in rule:
        if rule["expected-result"] != self.is_rule_check_successfull:
          logging.critical("-----------------------------------------------------------------------------")
          logging.critical("Unit test failed ! Expected result was " + str(rule["expected-result"]) + " and we got " + str(self.is_rule_check_successfull))
          print(rule)
          logging.critical("-----------------------------------------------------------------------------")
        else: 
          # Counter used to display the number of rules matching expected result
          # either failed of successfull, but as expected (handy for unit tests)
          rule_as_expected_counter += 1

      # Test if the label field is defined, if yes we have to output a message
      # for this rule with the result of the check
      if "label" in rule:
        # Define an empty result
        label_check_result = ""
        # If the check is successful, set the label to OK
        if self.is_rule_check_successfull == False:
          label_check_result = "[ OK ]"
        else:
          # Otherwise set it to fail
          label_check_result = "[FAIL]"
        # And print the test number, label and result to stdout
        print(label_check_result + " " + rule["label"])

    #
    # Process the "allowed" rules group
    #
    for rule in self.project.check_definition["packages"]["allowed"]:
      # Rule counter used to display the total number of checked rules
      rule_counter += 1

      # Call the check package method
      self.check_package_rules(rule, allowed=True)

      # If the test was negative, then change the global result to false
      if self.is_rule_check_successfull == False:
        # Set the global failure flag
        self.is_check_successfull = False
        # Counter used to display the number of failed rules
        rule_failed_counter += 1
      else:
        # Counter used to display the number of successful rules
        rule_successfull_counter += 1

      # If the expected result variable has been defined, the compare it value
      # to the actual method result, and output a critical if different
      # expected-result value is used in unit testing context, and it should 
      # never be different unless something nasty is lurking inthe dark
      if "expected-result" in rule:
        if rule["expected-result"] != self.is_rule_check_successfull:
          logging.critical("-----------------------------------------------------------------------------")
          logging.critical("Unit test failed ! Expected result was " + str(rule["expected-result"]) + " and we got " + str(self.is_rule_check_successfull))
          print(rule)
          logging.critical("-----------------------------------------------------------------------------")
        else: 
          # Counter used to display the number of rules matching expected result
          # either failed of successfull, but as expected (handy for unit tests)
          rule_as_expected_counter += 1

      # Test if the label field is defined, if yes we have to output a message
      # for this rule with the result of the check
      if "label" in rule:
        # Define an empty result
        label_check_result = ""
        # If the check is successful, set the label to OK
        if self.is_rule_check_successfull == False:
          label_check_result = "[ OK ]"
        else:
          # Otherwise set it to fail
          label_check_result = "[FAIL]"
        # And print the test number, label and result to stdout
        print(label_check_result + " " + rule["label"])

# TODO traiter les paquet en rc ?

    # Output the execution summary
# TODO handle plural
# TODO handle none for expected in case the  is no unit tests
    print("")
    print("Package check execution summary")
    print(". Processed " + str(rule_counter) + " rules")
    print(". " + str(rule_successfull_counter) + " were successfull")
    print(". " + str(rule_failed_counter) + " failed")
    print(". " + str(rule_as_expected_counter) + " ran as expected")
    print("")


  # -------------------------------------------------------------------------
  #
  # check_package_rules
  #
  # -------------------------------------------------------------------------
  def check_package_rules(self, rule, mandatory = None, forbidden = None, allowed = None):
    """This method is in charge of contolling if the rules defined for a
    given package are verified or not. It uses the same constraint definitions
    and structure as in check_packages method.
    """
  
    # Reset the package result. This is used mostly for unit testting and 
    # to track if the result was the expected one
    self.is_rule_check_successfull = True

    # First let's control that all keywords (key dictionnaires) are valid and know
    for keyword in rule:
      if keyword not in "name" "min-version" "max-version" "allowed-version" "blacklisted-version" "allowed-arch" "blacklisted-arch" "expected-result" "label":
        logging.error("Unknow keyword " + keyword + " when parsing packages rules. Rule is ignored")

    # Check if mandatory package is missing
    if mandatory == True and rule["name"] not in self.installed_packages:
      logging.error("Missing mandatory package : " + rule["name"])
      self.is_rule_check_successfull = False
      return

    # Check if forbidden package is installed
    if forbidden == True and rule["name"] in self.installed_packages:
      logging.error("Forbidden package is installed : " + rule["name"])
      self.is_rule_check_successfull = False
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
          logging.error("Version " + self.installed_packages[rule["name"]]["version"] + " of package is older than minimum allowed version " + rule["min-version"])
          self.is_rule_check_successfull = False
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
          logging.error("Version " + self.installed_packages[rule["name"]]["version"] + " of package is newer than maximum allowed version " + rule["max-version"])
          self.is_rule_check_successfull = False
        else:
          logging.debug("Version " + self.installed_packages[rule["name"]]["version"] + " of package is older than maximum allowed version " + rule["max-version"])

    # Check that version is in the list of allowed-version
    if "allowed-version" in rule:
      if rule["name"] in self.installed_packages: 
        if self.installed_packages[rule["name"]]["version"] not in rule["allowed-version"]: 
          logging.error("Version " + self.installed_packages[rule["name"]]["version"] + " of package " + rule["name"] + " is not allowed")
          self.is_rule_check_successfull = False
        else:
          logging.debug("Version " + self.installed_packages[rule["name"]]["version"] + " of package " + rule["name"] + " is allowed")

    # Check that version is not in the list of blacklisted versions
    if "blacklisted-version" in rule:
      if rule["name"] in self.installed_packages: 
        if self.installed_packages[rule["name"]]["version"] in rule["blacklisted-version"]: 
          logging.error("Version " + self.installed_packages[rule["name"]]["version"] + " of package " + rule["name"] + " is blacklisted")
          self.is_rule_check_successfull = False
        else:
          logging.debug("Version " + self.installed_packages[rule["name"]]["version"] + " of package " + rule["name"] + " is allowed")

    # Check that architecture is not in the list of blacklisted arch
    if "blacklisted-arch" in rule:
      if rule["name"] in self.installed_packages: 
        if self.installed_packages[rule["name"]]["arch"] in rule["blacklisted-arch"]: 
          logging.error("Package " + rule["name"] + " is blacklisted on architecture " + self.installed_packages[rule["name"]]["arch"])
          self.is_rule_check_successfull = False
        else:
          logging.debug("Package " + rule["name"] + " is not blacklisted on architecture " + self.installed_packages[rule["name"]]["arch"])

    # Check that version is in the list of allowed arch
    if "allowed-arch" in rule:
      if rule["name"] in self.installed_packages: 
        if self.installed_packages[rule["name"]]["arch"] not in rule["allowed-arch"]: 
          logging.error("Package " + rule["name"] + " is not allowed for architecture " + self.installed_packages[rule["name"]]["arch"])
          self.is_rule_check_successfull = False
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
    . mode           files attributes and mode (rwx)
    . target         only if type is symlink
    . empty          only for files and directories (zero sized for file, 
                     and no centent at all for directories)
    . md5            file (or symlink target) checksum computed with MD5
    . sha1           file (or symlink target) checksum computed with SHA1
    . sha256         file (or symlink target) checksum computed with SHA256

    """

    # Rule counter used to display the total number of checked rules
    rule_counter = 0
    
    # Counter used to display the number of successful rules
    rule_successfull_counter = 0

    # Counter used to display the number of failed rules
    rule_failed_counter = 0

    # Counter used to display the number of rules matching expected result
    # either failed of successfull, but as expected (handy for unit tests)
    rule_as_expected_counter = 0

    # Iterate the list of rules to check against installed files
    # Files will be checked on an individual basis, which is different of
    # packages. Package list can be retrieved with a single call to dpkg.
    # Retrieving the complete file list would cost too much
    for rule in self.project.check_definition["files"]["mandatory"]:
      # Rule counter used to display the total number of checked rules
      rule_counter += 1

      self.check_file_rules(rule, mandatory=True)

      # If the test was negative, then change the global result to false
      if self.is_rule_check_successfull == False:
        # Set the global failure flag
        self.is_check_successfull = False
        # Counter used to display the number of failed rules
        rule_failed_counter += 1
      else:
        # Counter used to display the number of successful rules
        rule_successfull_counter += 1

      # If the expected result variable has been defined, the compare it value
      # to the actual method result, and output a critical if different
      # expected-result value is used in unit testing context, and it should 
      # never be different unless something nasty is lurking inthe dark
      if "expected-result" in rule:
        if rule["expected-result"] != self.is_rule_check_successfull:
          logging.critical("-----------------------------------------------------------------------------")
          logging.critical("Unit test failed ! Expected result was " + str(rule["expected-result"]) + " and we got " + str(self.is_rule_check_successfull))
          print(rule)
          logging.critical("-----------------------------------------------------------------------------")
        else: 
          # Counter used to display the number of rules matching expected result
          # either failed of successfull, but as expected (handy for unit tests)
          rule_as_expected_counter += 1

      # Test if the label field is defined, if yes we have to output a message
      # for this rule with the result of the check
      if "label" in rule:
        # Define an empty result
        label_check_result = ""
        # If the check is successful, set the label to OK
        if self.is_rule_check_successfull == False:
          label_check_result = "[ OK ]"
        else:
          # Otherwise set it to fail
          label_check_result = "[FAIL]"
        # And print the test number, label and result to stdout
        print(label_check_result + " " + rule["label"])

    #
    # Process the "forbidden" rules group
    #
    for rule in self.project.check_definition["files"]["forbidden"]:
      # Rule counter used to display the total number of checked rules
      rule_counter += 1

      self.check_file_rules(rule, forbidden=True)

      # If the test was negative, then change the global result to false
      if self.is_rule_check_successfull == False:
        # Set the global failure flag
        self.is_check_successfull = False
        # Counter used to display the number of failed rules
        rule_failed_counter += 1
      else:
        # Counter used to display the number of successful rules
        rule_successfull_counter += 1

      # If the expected result variable has been defined, the compare it value
      # to the actual method result, and output a critical if different
      # expected-result value is used in unit testing context, and it should 
      # never be different unless something nasty is lurking inthe dark
      if "expected-result" in rule:
        if rule["expected-result"] != self.is_rule_check_successfull:
          logging.critical("-----------------------------------------------------------------------------")
          logging.critical("Unit test failed ! Expected result was " + str(rule["expected-result"]) + " and we got " + str(self.is_rule_check_successfull))
          print(rule)
          logging.critical("-----------------------------------------------------------------------------")
        else: 
          # Counter used to display the number of rules matching expected result
          # either failed of successfull, but as expected (handy for unit tests)
          rule_as_expected_counter += 1

      # Test if the label field is defined, if yes we have to output a message
      # for this rule with the result of the check
      if "label" in rule:
        # Define an empty result
        label_check_result = ""
        # If the check is successful, set the label to OK
        if self.is_rule_check_successfull == False:
          label_check_result = "[ OK ]"
        else:
          # Otherwise set it to fail
          label_check_result = "[FAIL]"
        # And print the test number, label and result to stdout
        print(label_check_result + " " + rule["label"])

    #
    # Process the "allowed" rules group
    #
    for rule in self.project.check_definition["files"]["allowed"]:
      # Rule counter used to display the total number of checked rules
      rule_counter += 1

      self.check_file_rules(rule, allowed=True)

      # If the test was negative, then change the global result to false
      if self.is_rule_check_successfull == False:
        # Set the global failure flag
        self.is_check_successfull = False
        # Counter used to display the number of failed rules
        rule_failed_counter += 1
      else:
        # Counter used to display the number of successful rules
        rule_successfull_counter += 1

      # If the expected result variable has been defined, the compare it value
      # to the actual method result, and output a critical if different
      # expected-result value is used in unit testing context, and it should 
      # never be different unless something nasty is lurking inthe dark
      if "expected-result" in rule:
        if rule["expected-result"] != self.is_rule_check_successfull:
          logging.critical("-----------------------------------------------------------------------------")
          logging.critical("Unit test failed ! Expected result was " + str(rule["expected-result"]) + " and we got " + str(self.is_rule_check_successfull))
          print(rule)
          logging.critical("-----------------------------------------------------------------------------")
        else: 
          # Counter used to display the number of rules matching expected result
          # either failed of successfull, but as expected (handy for unit tests)
          rule_as_expected_counter += 1

      # Test if the label field is defined, if yes we have to output a message
      # for this rule with the result of the check
      if "label" in rule:
        # Define an empty result
        label_check_result = ""
        # If the check is successful, set the label to OK
        if self.is_rule_check_successfull == False:
          label_check_result = "[ OK ]"
        else:
          # Otherwise set it to fail
          label_check_result = "[FAIL]"
        # And print the test number, label and result to stdout
        print(label_check_result + " " + rule["label"])

# TODO handle plural
# TODO handle none for expected in case the  is no unit tests

    print("")
    print("File check execution summary")
    print(". Processed " + str(rule_counter) + " rules")
    print(". " + str(rule_successfull_counter) + " were successfull")
    print(". " + str(rule_failed_counter) + " failed")
    print(". " + str(rule_as_expected_counter) + " ran as expected")
    print("")


  # -------------------------------------------------------------------------
  #
  # check_file_rules
  #
  # -------------------------------------------------------------------------
  def check_file_rules(self, rule, mandatory = None, forbidden = None, allowed = None):
    """This method is in charge of contolling if the rules defined for a
    given file, directory or symlink are verified or not. It uses the same 
    constraint definitions and structure as in check_files method.
    """
  
    # Reset the package result. This is used mostly for unit testting and 
    # to track if the result was the expected one
    self.is_rule_check_successfull = True

    # First let's control that all keywords (key dictionnaires) are valid and know
    for keyword in rule:
      if keyword not in "path" "type" "owner" "group" "mode" "target" "empty" "md5" "sha1" "sha256" "expected-result" :
        logging.error("Unknow keyword " + keyword + " when parsing filess rules. Rule is ignored")
        logging.error("Rule is " + str(rule))
        
    # Let's check there is a path...
    if "path" not in rule:
      logging.error("Undefined path when parsing file rules. Rule is ignored")

    #
    # Set some default values if they are missing from the rule
    #

    # Default type is file
    if "type" not in rule:
      rule["type"] = "file"
    else:
      if rule["type"] not in "file" "directory" "symlink":
        logging.error("Unknow type " + rule["type"] + " when parsing file rule. Rule is ignored")
        logging.error("Rule is "+ str(rule))
        self.is_rule_check_successfull = False
        return      

    # Target path is not an attribute, but a computed variable. It contains
    # the path to file or directory ultimatly pointed by symlinks. Computing
    # This variable has to be recursive since a link can point to a link
    rule["path"] = self.project.rootfs_mountpoint + rule["path"] 
    rule["target_path"] = rule["path"]
    while os.path.islink(rule["target_path"]):
      rule["target_path"] = os.readlink(rule["target_path"])

    # Check if mandatory package is missing
    if mandatory == True:
# TODO inverser les tests et skip derriere le cas qui marche, par defaut erreur
        # Check for mandatoy directory
        if os.path.isdir(rule["path"]) == False and rule["type"] == "directory":
          logging.info("Missing mandatory directory : " + rule["path"])
          self.is_rule_check_successfull = False
          return

        # Check for mandatoy symlink
        if os.path.islink(rule["path"]) == False and rule["type"] == "symlink":
          logging.info("Missing mandatory symlink : " + rule["path"])
          self.is_rule_check_successfull = False
          return

        # Check for mandatoy file
        if os.path.isfile(rule["path"]) == False and rule["type"] == "file":
          logging.info("Missing mandatory file : " + rule["path"])
          self.is_rule_check_successfull = False
          return

    # Check if forbidden files are installed
    if forbidden == True:
        # Check for forbidden directory
        if os.path.isdir(rule["path"]) == True and rule["type"] == "directory":
          logging.info("Forbidden directory exists : " + rule["path"])
          self.is_rule_check_successfull = False
          return

        # Check for forbidden symlink
        if os.path.islink(rule["path"]) == True and rule["type"] == "symlink":
          logging.info("Forbidden symlink exists : " + rule["path"])
          self.is_rule_check_successfull = False
          return

        # Check for forbidden file
        if os.path.isfile(rule["path"]) == True and rule["type"] == "file":
          logging.info("Forbidden file exists : " + rule["path"])
          self.is_rule_check_successfull = False
          return

    # Check the type of the object (can be file directory or symlink)
    if "type" in rule:
      if os.path.isdir(rule["path"]) == False and rule["type"] == "directory":
        logging.info("Object " + rule["path"] + " is not a directory")
        self.is_rule_check_successfull = False

      # Check for mandatoy symlink
      if os.path.islink(rule["path"]) == False and rule["type"] == "symlink":
        logging.info("Object " + rule["path"] + " is not a symlink")
        self.is_rule_check_successfull = False

      # Check for mandatoy file
      if os.path.isfile(rule["path"]) == False and rule["type"] == "file":
        logging.info("Object " + rule["path"] + " is not a file")
        self.is_rule_check_successfull = False

    # Check the owner of the object
    if "owner" in rule:
      # Retrieve the uid from the stat call
      uid = os.stat(rule["path"]).st_uid

      # Compare it to the owner from the rule
      if uid != rule["owner"]:
          logging.error("File " + rule["path"] + " owner is invalid. UID is " + str(uid) + " instead of " + rule["owner"])
          self.is_rule_check_successfull = False

    # Check the group of the object
    if "group" in rule:
      # Retrieve the gid from the stat call
      gid = os.stat(rule["path"]).st_gid

      # Compare it to the owner from the rule
      if gid != rule["group"]:
          logging.error("File " + rule["path"] + " group is invalid. GID is " + str(gid) + " instead of " + rule["group"])
          self.is_rule_check_successfull = False

    # Check the mode of the object
    if "mode" in rule:
      # Retrieve the mode from the stat call
      mode = os.stat(rule["path"]).st_mode

      # Compare it to the owner from the rule
      if mode != rule["mode"]:
          logging.error("File " + rule["path"] + " mode is invalid. Mode is " + str(mode) + " instead of " + rule["mode"])
          self.is_rule_check_successfull = False

    # Check the target of the symlink
    if "target" in rule:
      print ("TODO target")

    # Check the group of the object
    if "empty" in rule:
      # Check if the file exist. Use the target path to expand symlinks
      if os.path.isfile(rule["target_path"]) == False:
        logging.info("Missing target file : " + rule["target_path"])
        self.is_rule_check_successfull = False
        return

      # Retrieve the size from the stat call
      size = os.stat(rule["target_path"]).st_mode

      # Check if the file exist. Use the target path to expand symlinks
      if os.path.isfile(rule["target_path"]) == False:
        logging.info("Missing target file : " + rule["target_path"])
        self.is_rule_check_successfull = False
        return
      # Compare it to the owner from the rule
      if rule["empty"] == True and size != 0:
          logging.error("File " + rule["path"] + " is not empty. Size is " + str(size) + " instead of 0")
          self.is_rule_check_successfull = False

    # Check the md5 hash of the target
    if "md5" in rule:

      # Check if the file exist. Use the target path to expand symlinks
      if os.path.isfile(rule["target_path"]) == False:
        logging.info("Missing target file : " + rule["target_path"])
        self.is_rule_check_successfull = False
        return

      # Create the hasher used to parse file and compute hash
      hasher = hashlib.md5()

      # Open file in read binary mode
      with open(rule["path"], 'rb') as file_to_hash:

        # Create the buffer for file reading
        buffer = file_to_hash.read(self.block_size)

        # Iterate the file reading. Each time it loops, it updates the hasher 
        # buffer, appending data just read
        while len(buffer) > 0:
          hasher.update(buffer)
          buffer = file_to_hash.read(self.block_size)

        # Compare the hash to the rule, and set the check flag if needed
        if rule["md5"] != hasher.hexdigest():
            logging.error("File " + rule["path"] + " has an invalid MD5 hash. MD5 is " + hasher.hexdigest() + " instead of " + rule["md5"])
            self.is_rule_check_successfull = False
          
    # Check the sha1 hash of the target
    if "sha1" in rule:

      # Check if the file exist. Use the target path to expand symlinks
      if os.path.isfile(rule["target_path"]) == False:
        logging.info("Missing target file : " + rule["target_path"])
        self.is_rule_check_successfull = False
        return

      # Create the hasher used to parse file and compute hash
      hasher = hashlib.sha1()

      # Open file in read binary mode
      with open(rule["path"], 'rb') as file_to_hash:

        # Create the buffer for file reading
        buffer = file_to_hash.read(self.block_size)

        # Iterate the file reading. Each time it loops, it updates the hasher 
        # buffer, appending data just read
        while len(buffer) > 0:
          hasher.update(buffer)
          buffer = file_to_hash.read(self.block_size)

        # Compare the hash to the rule, and set the check flag if needed
        if rule["sha1"] != hasher.hexdigest():
            logging.error("File " + rule["path"] + " has an invalid SHA1 hash. SHA1 is " + hasher.hexdigest() + " instead of " + rule["sha1"])
            self.is_rule_check_successfull = False
          
    # Check the sha256 hash of the target
    if "sha256" in rule:

      # Check if the file exist. Use the target path to expand symlinks
      if os.path.isfile(rule["target_path"]) == False:
        logging.info("Missing target file : " + rule["target_path"])
        self.is_rule_check_successfull = False
        return

      # Create the hasher used to parse file and compute hash
      hasher = hashlib.sha256()

      # Open file in read binary mode
      with open(rule["path"], 'rb') as file_to_hash:

        # Create the buffer for file reading
        buffer = file_to_hash.read(self.block_size)

        # Iterate the file reading. Each time it loops, it updates the hasher 
        # buffer, appending data just read
        while len(buffer) > 0:
          hasher.update(buffer)
          buffer = file_to_hash.read(self.block_size)

        # Compare the hash to the rule, and set the check flag if needed
        if rule["sha256"] != hasher.hexdigest():
            logging.error("File " + rule["path"] + " has an invalid SHA256 hash. SHA256 is " + hasher.hexdigest() + " instead of " + rule["sha256"])
            self.is_rule_check_successfull = False
    