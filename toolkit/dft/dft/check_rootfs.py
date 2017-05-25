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

""" This module provides functionnalities used to control the content of the rootfs
according to a set of rules defined in a Yaml configuration file. Rules can be used to define
mandatory ites (files or packages), forbidden or optional ones, and a set of check upon
attributes and content.
"""

import os
import subprocess
import stat
import hashlib
from cli_command import CliCommand
from model import Key

#
#    Class CheckRootFS
#
class CheckRootFS(CliCommand):
  """This class implements method needed to check the base OS content.

  The content of the rootfs can be checked for mising or forbidden
  packages, files, directories and symlink. Attributes, versions and
  content can also be checked
  """
  # pylint: disable=too-many-instance-attributes

  # -------------------------------------------------------------------------
  #
  # __init__
  #
  # -------------------------------------------------------------------------
  def __init__(self, dft, project):
    """Default constructor
    """

    # Initialize ancestor
    CliCommand.__init__(self, dft, project)

    # Initialize a dictionnary to hold the list of installed packages
    self.installed_packages = {}

    # By default the check is successfull since not rules were checked
    # This boolean will be set to False (meaning check failed) as soon as a
    # rule verification will fail
    self.is_check_successfull = True

    # This variable is used to store the result of a single rule check
    # The variable value is reset for each loop, while the scope of the
    # previous one is the whole execution
    self.is_rule_check_successfull = True

    # Rule counter used to display the total number of checked rules
    self.rule_counter = 0

    # Counter used to display the number of successful rules
    self.rule_successfull_counter = 0

    # Counter used to display the number of failed rules
    self.rule_failed_counter = 0

    # Counter used to display the number of rules matching expected result
    # either failed of successfull, but as expected (handy for unit tests)
    self.rule_as_expected_counter = 0

    # Size of block used to read files when computing hashes
    self.block_size = 65536



  # -------------------------------------------------------------------------
  #
  # reset_rule_check_statistics
  #
  # -------------------------------------------------------------------------
  def reset_rule_check_statistics(self):
    """This method reset all the rules checking statitics. It has to be called
    at the begining of the file rule processing loop (not in a rule
    implentation, but in the top level loop)
    """
    # Rule counter used to display the total number of checked rules
    self.rule_counter = 0

    # Counter used to display the number of successful rules
    self.rule_successfull_counter = 0

    # Counter used to display the number of failed rules
    self.rule_failed_counter = 0

    # Counter used to display the number of rules matching expected result
    # either failed of successfull, but as expected (handy for unit tests)
    self.rule_as_expected_counter = 0

  # -------------------------------------------------------------------------
  #
  # process_rule_checking_output
  #
  # -------------------------------------------------------------------------
  def process_rule_checking_output(self, rule):
    """This method implement the process the results of a check rule call.
    It provides statitistics counter update, expected_result handling and
    label output method.

    All this code has been isolated in a single method since it is called from
    both package and file rule checking, several time each (one cal for
    mandatory, forbidden and allowed items).
    """

    # Rule counter used to display the total number of checked rules
    self.rule_counter += 1

    # If the test was negative, then change the global result to false
    if not self.is_rule_check_successfull:
      # Set the global failure flag
      self.is_check_successfull = False
      # Counter used to display the number of failed rules
      self.rule_failed_counter += 1
    else:
      # Counter used to display the number of successful rules
      self.rule_successfull_counter += 1

    # If the expected result variable has been defined, the compare it value
    # to the actual method result, and output a critical if different
    # expected_result value is used in unit testing context, and it should
    # never be different unless something nasty is lurking inthe dark
    if "expected-result" in rule:
      if rule["expected-result"] != self.is_rule_check_successfull:
        self.project.logging.critical("--------------------------------------------------------")
        self.project.logging.critical("Unit test failed ! Expected result was " +
                                      str(rule["expected_result"]) +
                                      " and we got " +
                                      str(self.is_rule_check_successfull))
        self.project.logging.debug(rule)
        self.project.logging.critical("--------------------------------------------------------")
      else:
        # Counter used to display the number of rules matching expected result
        # either failed of successfull, but as expected (handy for unit tests)
        self.rule_as_expected_counter += 1

    # Test if the label field is defined, if yes we have to output a message
    # for this rule with the result of the check
    if "label" in rule:
      # Define an empty result
      label_check_result = ""
      # If the check is successful, set the label to OK
      if self.is_rule_check_successfull:
        label_check_result = "[ OK ]"
      else:
        # Otherwise set it to fail
        label_check_result = "[FAIL]"
      # And print the test number, label and result to stdout
      print(label_check_result + " " + rule["label"])



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
    if self.use_qemu_static:
      # QEMU is used, and we have to install it into the target
      self.setup_qemu()

    #
    # Check the packages
    #
    if self.project.check_def != None and "packages" in self.project.check_def:
      self.project.logging.debug("Packages check is activated")
      self.check_packages()
    else:
      self.project.logging.info("Packages check generation is deactivated")

    #
    # Check the files
    #
    if self.project.check_def != None and "files" in self.project.check_def:
      self.project.logging.debug("Files check is activated")
      self.check_files()
    else:
      self.project.logging.info("Files check generation is deactivated")

    # Remove QEMU if it has been isntalled. It has to be done in the end
    # since some cleanup tasks could need QEMU
    if self.use_qemu_static:
      self.cleanup_qemu()

    # Check the final status and return an error if necessary
    if not self.is_check_successfull:
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
    . min_version          => LOWER versions CAN'T be installed
    . max_version          => MORE RECENT versions CAN'T be installed
    . allowed_version      => If installed, version MUST be one of the given
                              version in the list
    . blacklisted_version  => NONE of the given version CAN be installed
                              it is a list
    - allowed_arch         => The packages is allowed only on the given archs
    - blacklisted_arch     => The packages is blacklisted on the given archs
    """

    self.project.logging.info("starting to check installed packages")

    # Generate the dpkg command to retrieve the list of installed packages
    sudo_command = "LANG=C sudo chroot " + self.project.rootfs_mountpoint
    sudo_command += " dpkg -l | tail -n +6"
    pkglist = self.execute_command(sudo_command)

    # Iterate the output of the dpkg process and build the dictionnary of
    # all installed packages
    for binaryline in pkglist.splitlines():
      # Each fields is stored into a variable to easy manipulation and
      # simplify code. First get the array of words converted to UTF-8
      line = binaryline.decode('utf-8').split()

      # Extract each fields
      pkg_status = line[0]
      pkg_name = line[1]
      pkg_version = line[2]
      pkg_arch = line[3]

      # Build a dictionnary, using package name as main key
      self.installed_packages[pkg_name] = {'status':pkg_status,
                                           'version':pkg_version,
                                           'arch':pkg_arch}

    # Check the installation constraint (mandatory-only, allow-optional or no-constraint)
    self.check_installation_constraint()

    # Reset the rules statistics before starting to itare the list of rules
    self.reset_rule_check_statistics()

    #
    # Now iterate the list of rules to check against installed packages
    # Process the "mandatory" rules group
    #
    for rule in self.project.check_def["packages"]["mandatory"]:
      # Call the check package method
      self.check_package_rules(rule, mandatory=True)

      # Process the check results (update counters and output information)
      self.process_rule_checking_output(rule)

    #
    # Process the "forbidden" rules group
    #
    for rule in self.project.check_def["packages"]["forbidden"]:
      # Call the check package method
      self.check_package_rules(rule, forbidden=True)

      # Process the check results (update counters and output information)
      self.process_rule_checking_output(rule)

    #
    # Process the "allowed" rules group
    #
    for rule in self.project.check_def["packages"]["allowed"]:
      # Call the check package method
      self.check_package_rules(rule)

      # Process the check results (update counters and output information)
      self.process_rule_checking_output(rule)

# TODO traiter les paquet en rc ?

    # Output the execution summary
# TODO handle none for expected in case the  is no unit tests
    print("")
    print("Package check execution summary")
    print(". Processed " + str(self.rule_counter) + " rules")
    print(". " + str(self.rule_successfull_counter) + " were successfull")
    print(". " + str(self.rule_failed_counter) + " failed")
    print(". " + str(self.rule_as_expected_counter) + " ran as expected")
    print("")

  # -------------------------------------------------------------------------
  #
  # check_installation_constraint
  #
  # -------------------------------------------------------------------------
  def check_installation_constraint(self):
    """This method is in charge of chcking that the installed packages are
    compliant with the constaint defined in the configuration section.
    Constraint can be :
    - mandatory-only  (only packages listed in the the mandatory section can
                       be installed)
    - allow-optional  (only listed packages can be installed aither mandatory
                       or optional)
    - no-constraint   (any packages can b installed even if not listed)

    default value is no-constraint

    The method first build a dictionnary of allowed packages from the set
    of rules, then for each installed package, it checks if the packaeg is in
    the list.
    """

    # Initialize the local variable containing the list of allowed packages
    list_allowed_packages = {}

    # Checks that the configuration section is defined
    if "configuration" in self.project.check_def:
      # And that constraint is defined
      if "installation_constraint" in self.project.check_def["configuration"]:
        # Now check the defined contraint is valid (ie: no gizmo value)
        if self.project.check_def["configuration"]["installation_constraint"] not in\
          "mandatory-only" "allow-optional" "no-constraint":
          self.project.logging.error("unknown installation constraint " + \
                                     self.project.check_def["configuration"]\
                                     ["installation_constraint"])
          return False
        # If we reach this code, then there is a valid constaint defined
        else:
          # IF constraint is no-constraint there is nothing to do
          if self.project.check_def["configuration"]["installation_constraint"] == "no-constaint":
            self.project.logging.debug("installation constraint is " + \
                                       self.project.check_def["configuration"]\
                                                             ["installation_constraint"])
            return True

          # Build the list of packages defined in the mandatory section. They
          # will be inthe list whatever is the constraint
          for rule in self.project.check_def["packages"]["mandatory"]:
            list_allowed_packages[rule["name"]] = True

          # Check if the optional packages are allowed, if yes add then to the list
          if self.project.check_def["configuration"]["installation_constraint"] == "allow-optional":
            for rule in self.project.check_def["packages"]["allowed"]:
              list_allowed_packages[rule["name"]] = True
      else:
        self.project.logging.debug("no installation_constraint")
    else:
      self.project.logging.debug("no configuration section")

    # Iterate the list of installed packages and check if they belong to the
    # list of allowed packages
    for pkg in self.installed_packages:
      if pkg not in list_allowed_packages:
        # No... thus set the global failure flag
        self.is_check_successfull = False
        self.project.logging.info("Package " + pkg +
                                  " is installed but not allowed by installation constraint.")



  # -------------------------------------------------------------------------
  #
  # check_package_rules
  #
  # -------------------------------------------------------------------------
  def check_package_rules(self, rule, mandatory=None, forbidden=None):
    """This method is in charge of contolling if the rules defined for a
    given package are verified or not. It uses the same constraint definitions
    and structure as in check_packages method.
    """

    self.project.logging.debug("")
    self.project.logging.debug("Enter check_package_rules")

    # Reset the package result. This is used mostly for unit testting and
    # to track if the result was the expected one
    self.is_rule_check_successfull = True

    # First let's control that all keywords (key dictionnaires) are valid and know
    for keyword in rule:
      if keyword not in "name" "min_version" "max_version" "allowed_version" "blacklisted_version"\
                        "allowed_arch" "blacklisted_arch" "expected_result" "label":
        self.project.logging.error("Unknown keyword " + keyword +
                                   " when parsing packages rules. Rule is ignored")

    # Check if mandatory package is missing
    if mandatory and rule["name"] not in self.installed_packages:
      self.project.logging.error("Missing mandatory package : " + rule["name"])
      self.is_rule_check_successfull = False
      return

    # Check if forbidden package is installed
    if forbidden and rule["name"] in self.installed_packages:
      self.project.logging.error("Forbidden package is installed : " + rule["name"])
      self.is_rule_check_successfull = False
      return

    # Check version if higher or equal than min version
    if "min_version" in rule:
      return_code = 0
      if rule["name"] in self.installed_packages:
        # Generate the dpkg command to compare the versions
        dpkg_command = "dpkg --compare-versions " + rule["min_version"]
        dpkg_command += " lt " + self.installed_packages[rule["name"]]["version"]

        # We have to protect the subprocess in a try except block since dpkg
        # will return 1 if the check is invalid
        try:
          compare_result = subprocess.run(dpkg_command, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, shell=True,
                                          check=True, universal_newlines=False)
          return_code = compare_result.returncode

        # Catch the execution exception and set return_code to something else than zero
        except subprocess.CalledProcessError:
          return_code = 1

        # If the result is not ok, then output an info an go on checking next keyword
        if return_code > 0:
          self.project.logging.error("Version " + self.installed_packages[rule["name"]]["version"] +
                                     " of package is older than minimum allowed version " +
                                     rule["min_version"])
          return

        else:
          self.project.logging.debug("Version " + self.installed_packages[rule["name"]]["version"] +
                                     " of package is newer than minimum allowed version " +
                                     rule["min_version"])

    # Check version if lower or equal than max version
    if "max_version" in rule:
      return_code = 0
      if rule["name"] in self.installed_packages:
          # Generate the dpkg command to compare the versions
        dpkg_command = "dpkg --compare-versions " + rule["max_version"]
        dpkg_command += " gt " + self.installed_packages[rule["name"]]["version"]

        # We have to protect the subprocess in a try except block since dpkg
        # will return 1 if the check is invalid
        try:
          compare_result = subprocess.run(dpkg_command, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, shell=True,
                                          check=True, universal_newlines=False)
          return_code = compare_result.returncode

        # Catch the execution exception and set return_code to something else than zero
        except subprocess.CalledProcessError:
          return_code = 1

        # If the result is not ok, then output an info an go on checking next keyword
        if return_code > 0:
          self.project.logging.error("Version " + self.installed_packages[rule["name"]]["version"] +
                                     " of package is newer than maximum allowed version " +
                                     rule["max_version"])
          self.is_rule_check_successfull = False
          return
        else:
          self.project.logging.debug("Version " + self.installed_packages[rule["name"]]["version"] +
                                     " of package is older than maximum allowed version " +
                                     rule["max_version"])

    # Check that version is in the list of allowed_version
    if "allowed_version" in rule:
      if rule["name"] in self.installed_packages:
        if self.installed_packages[rule["name"]]["version"] not in rule["allowed_version"]:
          self.project.logging.error("Version " + self.installed_packages[rule["name"]]["version"] +
                                     " of package " + rule["name"] + " is not allowed")
          self.is_rule_check_successfull = False
          return
        else:
          self.project.logging.debug("Version " + self.installed_packages[rule["name"]]["version"] +
                                     " of package " + rule["name"] + " is allowed")

    # Check that version is not in the list of blacklisted versions
    if "blacklisted_version" in rule:
      if rule["name"] in self.installed_packages:
        if self.installed_packages[rule["name"]]["version"] in rule["blacklisted_version"]:
          self.project.logging.error("Version " + self.installed_packages[rule["name"]]["version"] +
                                     " of package " + rule["name"] + " is blacklisted")
          self.is_rule_check_successfull = False
          return
        else:
          self.project.logging.debug("Version " + self.installed_packages[rule["name"]]["version"] +
                                     " of package " + rule["name"] + " is allowed")

    # Check that architecture is not in the list of blacklisted arch
    if "blacklisted_arch" in rule:
      if rule["name"] in self.installed_packages:
        if self.installed_packages[rule["name"]]["arch"] in rule["blacklisted_arch"]:
          self.project.logging.error("Package " + rule["name"] +
                                     " is blacklisted on architecture " +
                                     self.installed_packages[rule["name"]]["arch"])
          self.is_rule_check_successfull = False
          return
        else:
          self.project.logging.debug("Package " + rule["name"] +
                                     " is not blacklisted on architecture " +
                                     self.installed_packages[rule["name"]]["arch"])

    # Check that version is in the list of allowed arch
    if "allowed_arch" in rule:
      if rule["name"] in self.installed_packages:
        if self.installed_packages[rule["name"]]["arch"] not in rule["allowed_arch"]:
          self.project.logging.error("Package " + rule["name"] +
                                     " is not allowed for architecture " +
                                     self.installed_packages[rule["name"]]["arch"])
          self.is_rule_check_successfull = False
          return
        else:
          self.project.logging.debug("Package " + rule["name"] +
                                     " is allowed for architecture " +
                                     self.installed_packages[rule["name"]]["arch"])

    self.project.logging.debug("Method check_package_rules returns " +
                               str(self.is_rule_check_successfull))
    self.project.logging.debug("")


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

    # Reset the rules statistics before starting to itare the list of rules
    self.reset_rule_check_statistics()

    # Iterate the list of rules to check against installed files
    # Files will be checked on an individual basis, which is different of
    # packages. Package list can be retrieved with a single call to dpkg.
    # Retrieving the complete file list would cost too much
    for rule in self.project.check_def["files"]["mandatory"]:
      # Call the check package method
      self.check_file_rules(rule, mandatory=True)

      # Process the check results (update counters and output information)
      self.process_rule_checking_output(rule)

    #
    # Process the "forbidden" rules group
    #
    for rule in self.project.check_def["files"]["forbidden"]:
      # Call the check package method
      self.check_file_rules(rule, forbidden=True)

      # Process the check results (update counters and output information)
      self.process_rule_checking_output(rule)

    #
    # Process the "allowed" rules group
    #
    for rule in self.project.check_def["files"]["allowed"]:
      # Call the check package method
      self.check_file_rules(rule, allowed=True)

      # Process the check results (update counters and output information)
      self.process_rule_checking_output(rule)

# TODO handle none for expected in case the  is no unit tests

    print("")
    print("File check execution summary")
    print(". Processed " + str(self.rule_counter) + " rules")
    print(". " + str(self.rule_successfull_counter) + " were successfull")
    print(". " + str(self.rule_failed_counter) + " failed")
    print(". " + str(self.rule_as_expected_counter) + " ran as expected")
    print("")


  # -------------------------------------------------------------------------
  #
  # check_file_rules
  #
  # -------------------------------------------------------------------------
  def check_file_rules(self, rule, mandatory=None, forbidden=None, allowed=None):
    """This method is in charge of contolling if the rules defined for a
    given file, directory or symlink are verified or not. It uses the same
    constraint definitions and structure as in check_files method.
    """

    # Reset the package result. This is used mostly for unit testting and
    # to track if the result was the expected one
    self.is_rule_check_successfull = True

    # First let's control that all keywords (key dictionnaires) are valid and know
    for keyword in rule:
      if keyword not in "path" "type" "owner" "group" "mode" "target" "empty" "md5" "sha1" "sha256"\
                        "expected-result" "label":
        self.project.logging.error("Unknow keyword " + keyword +
                                   " when parsing filess rules. Rule is ignored")
        self.project.logging.error("Rule is " + str(rule))

    # Let's check there is a path...
    if "path" not in rule:
      self.project.logging.error("Undefined path when parsing file rules. Rule is ignored")

    #
    # Set some default values if they are missing from the rule
    #

    # Default type is file
    if "type" not in rule:
      rule["type"] = "file"
    else:
      if rule["type"] not in "file" "directory" "symlink":
        self.project.logging.error("Unknown type " + rule["type"] +
                                   " when parsing file rule. Rule is ignored")
        self.project.logging.error("Rule is "+ str(rule))
        self.is_rule_check_successfull = False
        return

    # Target path is not an attribute, but a computed variable. It contains
    # the path to file or directory ultimatly pointed by symlinks. Computing
    # This variable has to be recursive since a link can point to a link
    rule["path"] = self.project.rootfs_mountpoint + rule["path"]
    rule["target_path"] = rule["path"]
    while os.path.islink(rule["target_path"]):
      self.project.logging.debug("Processing link " + rule["target_path"])
      target = os.path.dirname(rule["target_path"])
      target += "/" + os.readlink(rule["target_path"])
      rule["target_path"] = target
      self.project.logging.debug("Expended to " + rule["target_path"])

    # Finally get the absolute path
    rule["target_path"] = os.path.realpath(rule["target_path"])

    self.project.logging.debug("After expension target_path " + rule["path"] +
                               " became " + rule["target_path"])

    # Check if mandatory package is missing
    if mandatory:
# TODO inverser les tests et skip derriere le cas qui marche, par defaut erreur
      # Check for mandatoy directory
      if not os.path.isdir(rule["path"]) and rule["type"] == "directory":
        self.project.logging.info("Missing mandatory directory : " + rule["path"])
        self.is_rule_check_successfull = False
        return

      # Check for mandatoy symlink
      if not os.path.islink(rule["path"]) and rule["type"] == "symlink":
        self.project.logging.info("Missing mandatory symlink : " + rule["path"])
        self.is_rule_check_successfull = False
        return

      # Check for mandatoy file
      if not os.path.isfile(rule["path"]) and rule["type"] == "file":
        self.project.logging.info("Missing mandatory file : " + rule["path"])
        self.is_rule_check_successfull = False
        return

      # If target is defined, we have to check that it does not exist either
      if "target" in rule:
        if not os.path.isdir(rule["path"]) and not os.path.islink(rule["path"]) and \
           not os.path.isfile(rule["path"]):
          self.project.logging.info("Missing mandatory target : " + rule["target_path"])
          self.is_rule_check_successfull = False
          return

    # Check if forbidden files are installed
    if forbidden:
      # Check for forbidden directory
      if os.path.isdir(rule["path"]) and rule["type"] == "directory":
        self.project.logging.info("Forbidden directory exists : " + rule["path"])
        self.is_rule_check_successfull = False
        return

      # Check for forbidden symlink
      if os.path.islink(rule["path"]) and rule["type"] == "symlink":
        self.project.logging.info("Forbidden symlink exists : " + rule["path"])
        self.is_rule_check_successfull = False
        return

      # Check for forbidden file
      if os.path.isfile(rule["path"]) and rule["type"] == "file":
        self.project.logging.info("Forbidden file exists : " + rule["path"])
        self.is_rule_check_successfull = False
        return

    # Check the type of the object (can be file directory or symlink)
    if allowed:
      if not os.path.isdir(rule["path"]) and rule["type"] == "directory":
        self.project.logging.info("Object " + rule["path"] + " is not a directory")
        self.is_rule_check_successfull = False
        return

      # Check for mandatoy symlink
      if not os.path.islink(rule["path"]) and rule["type"] == "symlink":
        self.project.logging.info("Object " + rule["path"] + " is not a symlink")
        self.is_rule_check_successfull = False
        return

      # Check for mandatoy file
      if not os.path.isfile(rule["path"]) and rule["type"] == "file":
        self.project.logging.info("Object " + rule["path"] + " is not a file")
        self.is_rule_check_successfull = False
        return

    # Check the owner of the object
    if "owner" in rule:
      # Retrieve the uid from the stat call
      uid = os.stat(rule["path"]).st_uid

      # Compare it to the owner from the rule
      if str(uid) != rule["owner"]:
        self.project.logging.info("File " + rule["path"] + " owner is invalid. UID is " +
                                  str(uid) + " instead of " + rule["owner"])
        self.is_rule_check_successfull = False
        return

    # Check the group of the object
    if "group" in rule:
      # Retrieve the gid from the stat call
      gid = os.stat(rule["path"]).st_gid

      # Compare it to the owner from the rule
      if str(gid) != rule["group"]:
        self.project.logging.info("File " + rule["path"] + " group is invalid. GID is " +
                                  str(gid) + " instead of " + rule["group"])
        self.is_rule_check_successfull = False
        return

    # Check the mode of the object
    if "mode" in rule:
      # Retrieve the mode from the stat call
      mode = os.stat(rule["path"]).st_mode

      # Convert to octal with same representation as filesystem
      mode = oct(stat.S_IMODE(mode))

      # Replace initial 0o by 0 in order to match filesystem representation
      mode = str(mode).replace("0o", "0")

      # Compare it to the owner from the rule
      if mode != rule["mode"]:
        self.project.logging.info("File " + rule["path"] + " mode is invalid. Mode is " +
                                  str(mode) + " instead of " + rule["mode"])
        self.is_rule_check_successfull = False
        return

    # Check the target of the symlink
    if "target" in rule:
      if not os.path.isdir(rule["target_path"]) and not os.path.islink(rule["target_path"]) and \
         not os.path.isfile(rule["target_path"]):
        self.project.logging.info("Target " + rule["target_path"] + " does not exist")
        self.is_rule_check_successfull = False
        return

    # Check the group of the object
    if "empty" in rule:
      # Check if the file exist. Use the target path to expand symlinks
      if os.path.isfile(rule["target_path"]):
        # Retrieve the size from the stat call
        size = os.stat(rule["target_path"]).st_size

        # Compare it to the owner from the rule
        if rule["empty"] and size != 0:
          self.project.logging.info("File " + rule["target_path"] +
                                    " is not empty. Size is " + str(size) +
                                    " instead of 0")
          self.is_rule_check_successfull = False
          return

        if not rule["empty"] and size == 0:
          self.project.logging.info("File " + rule["target_path"] +
                                    " is not empty. Size is " + str(size) +
                                    " instead of 0")
          self.is_rule_check_successfull = False
          return
      else:
        if os.path.isdir(rule["target_path"]):
          # Retrieve the list of files
          size = len(os.listdir(rule["target_path"]))

          # Compare it to the owner from the rule
          if rule["empty"] and size != 0:
            self.project.logging.info("File " + rule["target_path"] +
                                      " is not empty. Size is " +
                                      str(size) + " instead of 0")
            self.is_rule_check_successfull = False
            return

          if not rule["empty"] and size == 0:
            self.project.logging.info("File " + rule["target_path"] +
                                      " is not empty. Size is " +
                                      str(size) + " instead of 0")
            self.is_rule_check_successfull = False
            return


          self.project.logging.debug("Directory " + rule["target_path"] +
                                     " contains " + str(size) + " files")
        else:
          self.project.logging.info("Unknown target (" + rule["type"] + ") " +
                                    rule["target_path"])
          self.is_rule_check_successfull = False
          return

    # Check the md5 hash of the target
    if "md5" in rule:

      # Check if the file exist. Use the target path to expand symlinks
      if not os.path.isfile(rule["target_path"]):
        self.project.logging.info("Missing target file : " + rule["target_path"])
        self.is_rule_check_successfull = False
        return

      # Create the hasher used to parse file and compute hash
      md5_hasher = hashlib.md5()

      # Open file in read binary mode
      with open(rule["path"], 'rb') as file_to_hash:

        # Create the buffer for file reading
        buffer = file_to_hash.read(self.block_size)

        # Iterate the file reading. Each time it loops, it updates the hasher
        # buffer, appending data just read
        while len(buffer) > 0:
          md5_hasher.update(buffer)
          buffer = file_to_hash.read(self.block_size)

        # Compare the hash to the rule, and set the check flag if needed
        if rule["md5"] != md5_hasher.hexdigest():
          self.project.logging.info("File " + rule["path"] + " has an invalid MD5 hash. hash is " +
                                    md5_hasher.hexdigest() + " instead of " + rule["md5"])
          self.is_rule_check_successfull = False
          return
        else:
          self.project.logging.debug("File " + rule["path"] + " has a valid MD5 hash. hash is " +
                                     md5_hasher.hexdigest())

    # Check the sha1 hash of the target
    if "sha1" in rule:

      # Check if the file exist. Use the target path to expand symlinks
      if not os.path.isfile(rule["target_path"]):
        self.project.logging.info("Missing target file : " + rule["target_path"])
        self.is_rule_check_successfull = False
        return

      # Create the hasher used to parse file and compute hash
      sha1_hasher = hashlib.sha1()

      # Open file in read binary mode
      with open(rule["path"], 'rb') as file_to_hash:

        # Create the buffer for file reading
        buffer = file_to_hash.read(self.block_size)

        # Iterate the file reading. Each time it loops, it updates the hasher
        # buffer, appending data just read
        while len(buffer) > 0:
          sha1_hasher.update(buffer)
          buffer = file_to_hash.read(self.block_size)

        # Compare the hash to the rule, and set the check flag if needed
        if rule["sha1"] != sha1_hasher.hexdigest():
          self.project.logging.info("File " + rule["path"] + " has an invalid SHA1 hash. hash is " +
                                    sha1_hasher.hexdigest() + " instead of " + rule["sha1"])
          self.is_rule_check_successfull = False
          return
        else:
          self.project.logging.debug("File " + rule["path"] + " has a valid SHA1 hash. hash is " +
                                     sha1_hasher.hexdigest())

    # Check the sha256 hash of the target
    if "sha256" in rule:

      # Check if the file exist. Use the target path to expand symlinks
      if not os.path.isfile(rule["target_path"]):
        self.project.logging.info("Missing target file : " + rule["target_path"])
        self.is_rule_check_successfull = False
        return

      # Create the hasher used to parse file and compute hash
      sha256_hasher = hashlib.sha256()

      # Open file in read binary mode
      with open(rule["path"], 'rb') as file_to_hash:

        # Create the buffer for file reading
        buffer = file_to_hash.read(self.block_size)

        # Iterate the file reading. Each time it loops, it updates the hasher
        # buffer, appending data just read
        while len(buffer) > 0:
          sha256_hasher.update(buffer)
          buffer = file_to_hash.read(self.block_size)

        # Compare the hash to the rule, and set the check flag if needed
        if rule["sha256"] != sha256_hasher.hexdigest():
          self.project.logging.info("File " + rule["path"] +
                                    " has an invalid SHA256 hash. SHA256 is " +
                                    sha256_hasher.hexdigest() + " instead of " + rule["sha256"])
          self.is_rule_check_successfull = False
          return
        else:
          self.project.logging.debug("File " + rule["path"] + " has a valid SHA256 hash. hash is " +
                                     sha256_hasher.hexdigest())
