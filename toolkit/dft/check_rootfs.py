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
from dft.cli_command import CliCommand
from dft.cli_command import Code
from dft.cli_command import Output
from dft.model import Key

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
  def process_rule_checking_output(self, rule, msg=""):
    """This method implement the process the results of a check rule call.
    It provides statitistics counter update, expected_result handling and
    label output method.

    All this code has been isolated in a single method since it is called from
    both package and file rule checking, several time each (one cal for
    mandatory, forbidden and allowed items).

    Optional message string (msg) is used to display hint for failures
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
    if Key.EXPECTED_RESULT.value in rule:
      if rule[Key.EXPECTED_RESULT.value] != self.is_rule_check_successfull:
        self.project.logging.debug("--------------------------------------------------------")
        self.project.logging.debug("Unit test failed ! Expected result was " +
                                   str(rule[Key.EXPECTED_RESULT.value]) +
                                   " and we got " +
                                   str(self.is_rule_check_successfull))
        self.project.logging.debug(rule)
        self.project.logging.debug("--------------------------------------------------------")
      else:
        # Counter used to display the number of rules matching expected result
        # either failed of successfull, but as expected (handy for unit tests)
        self.rule_as_expected_counter += 1

    # Test if the label field is defined, if yes we have to output a message
    # for this rule with the result of the check
    if Key.LABEL.value in rule:
      # Call the output method dealing with formatting result codes
      # Define an empty result
      label_check_result = ""
      # If the check is successful, set the label to OK
      if self.is_rule_check_successfull:
        self.output_string_with_result(rule[Key.LABEL.value], Code.SUCCESS)
      else:
        self.output_string_with_result(rule[Key.LABEL.value], Code.FAILURE)
        # If the hint message is defined, then output it
        if msg != "":
          self.display_test_result(msg)
    else:
      # Default message if no label is present
      if self.is_rule_check_successfull:
        self.output_string_with_result(".xXx.", Code.SUCCESS)
      else:
        self.output_string_with_result(".xXx.", Code.FAILURE)
        # If the hint message is defined, then output it
        if msg != "":
          self.display_test_result(msg)



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

    # Check that there is a check definition
    if self.project.check is None:
      self.project.logging.info("The project has no check information defined")
      return

    # Iterate the list of rule set, and call the dedicated method
    for rules in self.project.check:

      # Display startup mesage if defined
      if Key.MESSAGE_START.value in rules:
        self.project.logging.info(rules[Key.MESSAGE_START.value])

      #
      # Check the packages
      #
      if Key.PACKAGES.value in rules:
        self.project.logging.debug("Packages check is activated")
        self.check_packages(rules)
      else:
        self.project.logging.info("Packages check generation is deactivated")

      #
      # Check the files
      #
      if Key.FILES.value in rules:
        self.project.logging.debug("Files check is activated")
        self.check_files(rules)
      else:
        self.project.logging.info("Files check generation is deactivated")

      # Display end mesage if defined
      if Key.MESSAGE_END.value in rules:
        self.project.logging.info(rules[Key.MESSAGE_END.value])

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
  def check_packages(self, rules):
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

    self.project.logging.debug("starting to check installed packages")

    # Generate the dpkg command to retrieve the list of installed packages
    command = "LANG=C chroot " + self.project.get_rootfs_mountpoint()
    command += " dpkg -l | tail -n +6"
    pkglist = self.execute_command(command)

    # Iterate the output of the dpkg process and build the dictionnary of
    # all installed packages
    for binaryline in pkglist.splitlines():
      # Each fields is stored into a variable to easy manipulation and
      # simplify code. First get the array of words converted to UTF-8
      line = binaryline.decode(Key.UTF8.value).split()

      # Extract each fields
      pkg_status = line[0]
      pkg_name = line[1]
      pkg_version = line[2]
      pkg_arch = line[3]

      # Build a dictionnary, using package name as main key
      self.installed_packages[pkg_name] = {Key.STATUS.value:pkg_status,
                                           Key.VERSION.value:pkg_version,
                                           Key.ARCH.value:pkg_arch}

    # Check the installation constraint (mandatory-only, allow-optional or no-constraint)
    self.check_installation_constraint(rules)

    # Reset the rules statistics before starting to itare the list of rules
    self.reset_rule_check_statistics()

    #
    # Now iterate the list of rules to check against installed packages
    # Process the Key.MANDATORY.value rules group
    #
    for rule in rules[Key.PACKAGES.value][Key.MANDATORY.value]:
      # Call the check package method
      msg = self.check_package_rules(rule, mandatory=True)

      # Process the check results (update counters and output information)
      if msg != None:
        self.process_rule_checking_output(rule, msg)
      else:
        self.process_rule_checking_output(rule)

    #
    # Process the Key.FORBIDDEN.value rules group
    #
    for rule in rules[Key.PACKAGES.value][Key.FORBIDDEN.value]:
      # Call the check package method
      msg = self.check_package_rules(rule, forbidden=True)

      # Process the check results (update counters and output information)
      if msg != None:
        self.process_rule_checking_output(rule, msg)
      else:
        self.process_rule_checking_output(rule)

    #
    # Process the Key.ALLOWED.value rules group
    #
    for rule in rules[Key.PACKAGES.value][Key.ALLOWED.value]:
      # Call the check package method
      msg = self.check_package_rules(rule)

      # Process the check results (update counters and output information)
      if msg != None:
        self.process_rule_checking_output(rule, msg)
      else:
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
  def check_installation_constraint(self, rules):
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
    if Key.CONFIGURATION.value in rules:
      # And that constraint is defined
      if Key.INSTALLATION_CONSTRAINT.value in rules[Key.CONFIGURATION.value]:
        # Now check the defined contraint is valid (ie: no gizmo value)
        if rules[Key.CONFIGURATION.value][Key.INSTALLATION_CONSTRAINT.value] \
          not in [Key.MANDATORY_ONLY.value, Key.ALLOW_OPTIONAL.value, Key.NO_CONSTRAINT.value]:
#          not in "mandatory_only" "allow_optional" "allow_optional":
          self.project.logging.error("unknown installation constraint " + \
                                     rules[Key.CONFIGURATION.value]\
                                     [Key.INSTALLATION_CONSTRAINT.value])
          return False
        # If we reach this code, then there is a valid constaint defined
        else:
          # IF constraint is no-constraint there is nothing to do
          if rules[Key.CONFIGURATION.value][Key.INSTALLATION_CONSTRAINT.value] == \
                                                                            Key.NO_CONSTRAINT.value:
            self.project.logging.debug("installation constraint is " + \
                                       rules[Key.CONFIGURATION.value]\
                                            [Key.INSTALLATION_CONSTRAINT.value])
            return True

          # Build the list of packages defined in the mandatory section. They
          # will be inthe list whatever is the constraint
          for rule in rules[Key.PACKAGES.value][Key.MANDATORY.value]:
            list_allowed_packages[rule[Key.NAME.value]] = True

          # Check if the optional packages are allowed, if yes add then to the list
          if rules[Key.CONFIGURATION.value][Key.INSTALLATION_CONSTRAINT.value] == \
                                                                           Key.ALLOW_OPTIONAL.value:
            for rule in rules[Key.PACKAGES.value][Key.ALLOWED.value]:
              list_allowed_packages[rule[Key.NAME.value]] = True
      else:
        self.project.logging.debug("no " + Key.INSTALLATION_CONSTRAINT.value)
    else:
      self.project.logging.debug("no configuration section")

    # Iterate the list of installed packages and check if they belong to the
    # list of allowed packages
    for pkg in self.installed_packages:
      if pkg not in list_allowed_packages:
        # No... thus set the global failure flag
        self.is_check_successfull = False
        msg = "Package " + pkg + " is installed but not allowed by installation constraint."
        self.display_test_result(msg)



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
      if keyword not in [Key.NAME.value, Key.MIN_VERSION.value, Key.MAX_VERSION.value,
                         Key.ALLOWED_VERSION.value, Key.BLACKLISTED_VERSION.value,
                         Key.ALLOWED_ARCH.value, Key.BLACKLISTED_ARCH.value,
                         Key.EXPECTED_RESULT.value, Key.LABEL.value]:
        self.project.logging.error("Unknown keyword " + keyword +
                                   " when parsing packages rules. Rule is ignored")

    # Check if mandatory package is missing
    if mandatory and rule[Key.NAME.value] not in self.installed_packages:
      msg = "Missing mandatory package : " + rule[Key.NAME.value]
      self.is_rule_check_successfull = False
      return msg

    # Check if forbidden package is installed
    if forbidden and rule[Key.NAME.value] in self.installed_packages:
      msg = "Forbidden package is installed : " + rule[Key.NAME.value]
      self.is_rule_check_successfull = False
      return msg

    # Check version if higher or equal than min version
    if Key.MIN_VERSION.value in rule:
      return_code = 0
      if rule[Key.NAME.value] in self.installed_packages:
        # Generate the dpkg command to compare the versions
        dpkg_command = "dpkg --compare-versions " + rule[Key.MIN_VERSION.value]
        dpkg_command += " lt " + self.installed_packages[rule[Key.NAME.value]][Key.VERSION.value]

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
          self.project.logging.error("Version " + self.installed_packages[rule[Key.NAME.value]]\
                                     [Key.VERSION.value] + " of package is older than minimum " +
                                     "allowed version " + rule[Key.MIN_VERSION.value])
          return

        else:
          self.project.logging.debug("Version " + self.installed_packages[rule[Key.NAME.value]]\
                                     [Key.VERSION.value] + " of package is newer than minimum " +
                                     "allowed version " + rule[Key.MIN_VERSION.value])

    # Check version if lower or equal than max version
    if Key.MAX_VERSION.value in rule:
      return_code = 0
      if rule[Key.NAME.value] in self.installed_packages:
          # Generate the dpkg command to compare the versions
        dpkg_command = "dpkg --compare-versions " + rule[Key.MAX_VERSION.value]
        dpkg_command += " gt " + self.installed_packages[rule[Key.NAME.value]][Key.VERSION.value]

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
          self.project.logging.error("Version " + self.installed_packages[rule[Key.NAME.value]]\
                                     [Key.VERSION.value] + " of package is newer than maximum " +
                                     "allowed version " + rule[Key.MAX_VERSION.value])
          self.is_rule_check_successfull = False
          return
        else:
          self.project.logging.debug("Version " + self.installed_packages[rule[Key.NAME.value]]\
                                     [Key.VERSION.value] + " of package is older than maximum " +
                                     "allowed version " + rule[Key.MAX_VERSION.value])

    # Check that version is in the list of allowed_version
    if Key.ALLOWED_VERSION.value in rule:
      if rule[Key.NAME.value] in self.installed_packages:
        if self.installed_packages[rule[Key.NAME.value]][Key.VERSION.value] not in \
                                                                    rule[Key.ALLOWED_VERSION.value]:
          self.project.logging.error("Version " + self.installed_packages[rule[Key.NAME.value]]\
                                     [Key.VERSION.value] + " of package " + rule[Key.NAME.value] +
                                     " is not allowed")
          self.is_rule_check_successfull = False
          return
        else:
          self.project.logging.debug("Version " + self.installed_packages[rule[Key.NAME.value]]\
                                     [Key.VERSION.value] + " of package " + rule[Key.NAME.value] +
                                     " is allowed")

    # Check that version is not in the list of blacklisted versions
    if Key.BLACKLISTED_VERSION.value in rule:
      if rule[Key.NAME.value] in self.installed_packages:
        if self.installed_packages[rule[Key.NAME.value]][Key.VERSION.value] in \
                                                                rule[Key.BLACKLISTED_VERSION.value]:
          self.project.logging.error("Version " + self.installed_packages[rule[Key.NAME.value]]\
                                     [Key.VERSION.value] + " of package " + rule[Key.NAME.value] +
                                     " is blacklisted")
          self.is_rule_check_successfull = False
          return
        else:
          self.project.logging.debug("Version " + self.installed_packages[rule[Key.NAME.value]]\
                                     [Key.VERSION.value] + " of package " + rule[Key.NAME.value] +
                                     " is allowed")

    # Check that architecture is not in the list of blacklisted arch
    if Key.BLACKLISTED_ARCH.value in rule:
      if rule[Key.NAME.value] in self.installed_packages:
        if self.installed_packages[rule[Key.NAME.value]][Key.ARCH.value] in \
                                                                  rule[Key.BLACKLISTED_ARCH.value]:
          self.project.logging.error("Package " + rule[Key.NAME.value] +
                                     " is blacklisted on architecture " +
                                     self.installed_packages[rule[Key.NAME.value]][Key.ARCH.value])
          self.is_rule_check_successfull = False
          return
        else:
          self.project.logging.debug("Package " + rule[Key.NAME.value] +
                                     " is not blacklisted on architecture " +
                                     self.installed_packages[rule[Key.NAME.value]][Key.ARCH.value])

    # Check that version is in the list of allowed arch
    if Key.ALLOWED_ARCH.value in rule:
      if rule[Key.NAME.value] in self.installed_packages:
        if self.installed_packages[rule[Key.NAME.value]][Key.ARCH.value] not in \
                                                                      rule[Key.ALLOWED_ARCH.value]:
          self.project.logging.error("Package " + rule[Key.NAME.value] +
                                     " is not allowed for architecture " +
                                     self.installed_packages[rule[Key.NAME.value]][Key.ARCH.value])
          self.is_rule_check_successfull = False
          return
        else:
          self.project.logging.debug("Package " + rule[Key.NAME.value] +
                                     " is allowed for architecture " +
                                     self.installed_packages[rule[Key.NAME.value]][Key.ARCH.value])

    self.project.logging.debug("Method check_package_rules returns " +
                               str(self.is_rule_check_successfull))
    self.project.logging.debug("")


  # -------------------------------------------------------------------------
  #
  # check_files
  #
  # -------------------------------------------------------------------------
  def check_files(self, rules):
    """This method is in charge of contolling the files (and also
    directories and symlinks) installed in the rootfs according to the
    rules loaded from the configurtion file.

    Files in a term that identify any object in the file system. A 'file'
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
    for rule in rules[Key.FILES.value][Key.MANDATORY.value]:
      # Call the check package method
      self.check_file_rules(rule, mandatory=True)

      # Process the check results (update counters and output information)
      self.process_rule_checking_output(rule)

    #
    # Process the Key.FORBIDDEN.value rules group
    #
    for rule in rules[Key.FILES.value][Key.FORBIDDEN.value]:
      # Call the check package method
      self.check_file_rules(rule, forbidden=True)

      # Process the check results (update counters and output information)
      self.process_rule_checking_output(rule)

    #
    # Process the Key.ALLOWED.value rules group
    #
    for rule in rules[Key.FILES.value][Key.ALLOWED.value]:
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

    # Defines the output msg
    msg = ""

    # Reset the package result. This is used mostly for unit testting and
    # to track if the result was the expected one
    self.is_rule_check_successfull = True

    # First let's control that all keywords (key dictionnaires) are valid and know
    for keyword in rule:
      if keyword not in [Key.PATH.value, Key.TYPE.value, Key.OWNER.value, Key.GROUP.value,
                         Key.MODE.value, Key.TARGET.value, Key.EMPTY.value, Key.MD5.value,
                         Key.SHA1.value, Key.SHA256.value, Key.EXPECTED_RESULT.value,
                         Key.LABEL.value]:
        self.project.logging.error("Unknow keyword " + keyword +
                                   " when parsing filess rules. Rule is ignored")
        self.project.logging.error("Rule is " + str(rule))

    # Let's check there is a path...
    if Key.PATH.value not in rule:
      self.project.logging.error("Undefined path when parsing file rules. Rule is ignored")

    #
    # Set some default values if they are missing from the rule
    #

    # Default type is file
    if Key.TYPE.value not in rule:
      rule[Key.TYPE.value] = Key.FILE.value
    else:
      if rule[Key.TYPE.value] not in [Key.FILE.value, Key.DIRECTORY.value, Key.SYMLINK.value]:
        self.project.logging.error("Unknown type " + rule[Key.TYPE.value] +
                                   " when parsing file rule. Rule is ignored")
        self.project.logging.error("Rule is "+ str(rule))
        self.is_rule_check_successfull = False
        return

    # Target path is not an attribute, but a computed variable. It contains
    # the path to file or directory ultimatly pointed by symlinks. Computing
    # This variable has to be recursive since a link can point to a link
    rule[Key.PATH.value] = self.project.get_rootfs_mountpoint() + rule[Key.PATH.value]
    rule[Key.TARGET_PATH.value] = rule[Key.PATH.value]
    while os.path.islink(rule[Key.TARGET_PATH.value]):
      self.project.logging.debug("Processing link " + rule[Key.TARGET_PATH.value])
      target = os.path.dirname(rule[Key.TARGET_PATH.value])
      target += "/" + os.readlink(rule[Key.TARGET_PATH.value])
      rule[Key.TARGET_PATH.value] = target
      self.project.logging.debug("Expended to " + rule[Key.TARGET_PATH.value])

    # Finally get the absolute path
    rule[Key.TARGET_PATH.value] = os.path.realpath(rule[Key.TARGET_PATH.value])

    self.project.logging.debug("After expension target_path " + rule[Key.PATH.value] +
                               " became " + rule[Key.TARGET_PATH.value])

    # Check if mandatory package is missing
    if mandatory:
# TODO inverser les tests et skip derriere le cas qui marche, par defaut erreur
      # Check for mandatoy directory
      if not os.path.isdir(rule[Key.PATH.value]) and rule[Key.TYPE.value] == Key.DIRECTORY.value:
        self.project.logging.debug("Missing mandatory directory : " + rule[Key.PATH.value])
        self.is_rule_check_successfull = False
        return

      # Check for mandatoy symlink
      if not os.path.islink(rule[Key.PATH.value]) and rule[Key.TYPE.value] == Key.SYMLINK.value:
        self.project.logging.debug("Missing mandatory symlink : " + rule[Key.PATH.value])
        self.is_rule_check_successfull = False
        return

      # Check for mandatoy file
      if not os.path.isfile(rule[Key.PATH.value]) and rule[Key.TYPE.value] == Key.FILE.value:
        self.project.logging.info("Missing mandatory file : " + rule[Key.PATH.value])
        self.is_rule_check_successfull = False
        return

      # If target is defined, we have to check that it does not exist either
      if Key.TARGET.value in rule:
        if not os.path.isdir(rule[Key.PATH.value]) and not os.path.islink(rule[Key.PATH.value]) and\
           not os.path.isfile(rule[Key.PATH.value]):
          self.project.logging.debug("Missing mandatory target : " + rule[Key.TARGET_PATH.value])
          self.is_rule_check_successfull = False
          return

    # Check if forbidden files are installed
    if forbidden:
      # Check for forbidden directory
      if os.path.isdir(rule[Key.PATH.value]) and rule[Key.TYPE.value] == Key.DIRECTORY.value:
        self.project.logging.debug("Forbidden directory exists : " + rule[Key.PATH.value])
        self.is_rule_check_successfull = False
        return

      # Check for forbidden symlink
      if os.path.islink(rule[Key.PATH.value]) and rule[Key.TYPE.value] == Key.SYMLINK.value:
        self.project.logging.debug("Forbidden symlink exists : " + rule[Key.PATH.value])
        self.is_rule_check_successfull = False
        return

      # Check for forbidden file
      if os.path.isfile(rule[Key.PATH.value]) and rule[Key.TYPE.value] == Key.FILE.value:
        self.project.logging.debug("Forbidden file exists : " + rule[Key.PATH.value])
        self.is_rule_check_successfull = False
        return

    # Check the type of the object (can be file directory or symlink)
    if allowed:
      if not os.path.isdir(rule[Key.PATH.value]) and rule[Key.TYPE.value] == Key.DIRECTORY.value:
        self.project.logging.debug("Object " + rule[Key.PATH.value] + " is not a directory")
        self.is_rule_check_successfull = False
        return

      # Check for mandatoy symlink
      if not os.path.islink(rule[Key.PATH.value]) and rule[Key.TYPE.value] == Key.SYMLINK.value:
        self.project.logging.debug("Object " + rule[Key.PATH.value] + " is not a symlink")
        self.is_rule_check_successfull = False
        return

      # Check for mandatoy file
      if not os.path.isfile(rule[Key.PATH.value]) and rule[Key.TYPE.value] == Key.FILE.value:
        self.project.logging.debug("Object " + rule[Key.PATH.value] + " is not a file")
        self.is_rule_check_successfull = False
        return

    # Check the owner of the object
    if Key.OWNER.value in rule:
      # Retrieve the uid from the stat call
      uid = os.stat(rule[Key.PATH.value]).st_uid

      # Compare it to the owner from the rule
      if str(uid) != rule[Key.OWNER.value]:
        self.project.logging.debug("File " + rule[Key.PATH.value] + " owner is invalid. UID is " +
                                   str(uid) + " instead of " + rule[Key.OWNER.value])
        self.is_rule_check_successfull = False
        return

    # Check the group of the object
    if Key.GROUP.value in rule:
      # Retrieve the gid from the stat call
      gid = os.stat(rule[Key.PATH.value]).st_gid

      # Compare it to the owner from the rule
      if str(gid) != rule[Key.GROUP.value]:
        self.project.logging.debug("File " + rule[Key.PATH.value] + " group is invalid. GID is " +
                                   str(gid) + " instead of " + rule[Key.GROUP.value])
        self.is_rule_check_successfull = False
        return

    # Check the mode of the object
    if Key.MODE.value in rule:
      # Retrieve the mode from the stat call
      mode = os.stat(rule[Key.PATH.value]).st_mode

      # Convert to octal with same representation as filesystem
      mode = oct(stat.S_IMODE(mode))

      # Replace initial 0o by 0 in order to match filesystem representation
      mode = str(mode).replace("0o", "0")

      # Compare it to the owner from the rule
      if mode != rule[Key.MODE.value]:
        self.project.logging.debug("File " + rule[Key.PATH.value] + " mode is invalid. Mode is " +
                                   str(mode) + " instead of " + rule[Key.MODE.value])
        self.is_rule_check_successfull = False
        return

    # Check the target of the symlink
    if Key.TARGET.value in rule:
      if not os.path.isdir(rule[Key.TARGET_PATH.value]) and \
         not os.path.islink(rule[Key.TARGET_PATH.value]) and \
         not os.path.isfile(rule[Key.TARGET_PATH.value]):
        self.project.logging.debug("Target " + rule[Key.TARGET_PATH.value] + " does not exist")
        self.is_rule_check_successfull = False
        return

    # Check the group of the object
    if Key.EMPTY.value in rule:
      # Check if the file exist. Use the target path to expand symlinks
      if os.path.isfile(rule[Key.TARGET_PATH.value]):
        # Retrieve the size from the stat call
        size = os.stat(rule[Key.TARGET_PATH.value]).st_size

        # Compare it to the owner from the rule
        if rule[Key.EMPTY.value] and size != 0:
          self.project.logging.debug("File " + rule[Key.TARGET_PATH.value] +
                                     " is not empty. Size is " + str(size) +
                                     " instead of 0")
          self.is_rule_check_successfull = False
          return

        if not rule[Key.EMPTY.value] and size == 0:
          self.project.logging.debug("File " + rule[Key.TARGET_PATH.value] +
                                     " is not empty. Size is " + str(size) +
                                     " instead of 0")
          self.is_rule_check_successfull = False
          return
      else:
        if os.path.isdir(rule[Key.TARGET_PATH.value]):
          # Retrieve the list of files
          size = len(os.listdir(rule[Key.TARGET_PATH.value]))

          # Compare it to the owner from the rule
          if rule[Key.EMPTY.value] and size != 0:
            self.project.logging.debug("File " + rule[Key.TARGET_PATH.value] +
                                       " is not empty. Size is " +
                                       str(size) + " instead of 0")
            self.is_rule_check_successfull = False
            return

          if not rule[Key.EMPTY.value] and size == 0:
            self.project.logging.debug("File " + rule[Key.TARGET_PATH.value] +
                                       " is not empty. Size is " +
                                       str(size) + " instead of 0")
            self.is_rule_check_successfull = False
            return


          self.project.logging.debug("Directory " + rule[Key.TARGET_PATH.value] +
                                     " contains " + str(size) + " files")
        else:
          self.project.logging.info("Unknown target (" + rule[Key.TYPE.value] + ") " +
                                    rule[Key.TARGET_PATH.value])
          self.is_rule_check_successfull = False
          return

    # Check the md5 hash of the target
    if Key.MD5.value in rule:
      # Check if the file exist. Use the target path to expand symlinks
      if not os.path.isfile(rule[Key.TARGET_PATH.value]):
        self.project.logging.debug("Missing target file : " + rule[Key.TARGET_PATH.value])
        self.is_rule_check_successfull = False
        return

      # Create the hasher used to parse file and compute hash
      md5_hasher = hashlib.md5()

      # Open file in read binary mode
      with open(rule[Key.PATH.value], 'rb') as file_to_hash:

        # Create the buffer for file reading
        buffer = file_to_hash.read(self.block_size)

        # Iterate the file reading. Each time it loops, it updates the hasher
        # buffer, appending data just read
        while len(buffer) > 0:
          md5_hasher.update(buffer)
          buffer = file_to_hash.read(self.block_size)

        # Compare the hash to the rule, and set the check flag if needed
        if rule[Key.MD5.value] != md5_hasher.hexdigest():
          self.project.logging.debug("File " + rule[Key.PATH.value] + " has an invalid MD5 hash. " +
                                     "hash is " + md5_hasher.hexdigest() + " instead of " +
                                     rule[Key.MD5.value])
          self.is_rule_check_successfull = False
          return
        else:
          self.project.logging.debug("File " + rule[Key.PATH.value] + " has a valid MD5 hash. " +
                                     "hash is " + md5_hasher.hexdigest())

    # Check the sha1 hash of the target
    if Key.SHA1.value in rule:

      # Check if the file exist. Use the target path to expand symlinks
      if not os.path.isfile(rule[Key.TARGET_PATH.value]):
        self.project.logging.debug("Missing target file : " + rule[Key.TARGET_PATH.value])
        self.is_rule_check_successfull = False
        return

      # Create the hasher used to parse file and compute hash
      sha1_hasher = hashlib.sha1()

      # Open file in read binary mode
      with open(rule[Key.PATH.value], 'rb') as file_to_hash:

        # Create the buffer for file reading
        buffer = file_to_hash.read(self.block_size)

        # Iterate the file reading. Each time it loops, it updates the hasher
        # buffer, appending data just read
        while len(buffer) > 0:
          sha1_hasher.update(buffer)
          buffer = file_to_hash.read(self.block_size)

        # Compare the hash to the rule, and set the check flag if needed
        if rule[Key.SHA1.value] != sha1_hasher.hexdigest():
          self.project.logging.debug("File " + rule[Key.PATH.value] + " has an invalid SHA1 hash. " +
                                     "hash is " + sha1_hasher.hexdigest() + " instead of " +
                                     rule[Key.SHA1.value])
          self.is_rule_check_successfull = False
          return
        else:
          self.project.logging.debug("File " + rule[Key.PATH.value] + " has a valid SHA1 hash. " +
                                     "hash is " + sha1_hasher.hexdigest())

    # Check the sha256 hash of the target
    if Key.SHA256.value in rule:

      # Check if the file exist. Use the target path to expand symlinks
      if not os.path.isfile(rule[Key.TARGET_PATH.value]):
        msg = "Missing target file : " + rule[Key.TARGET_PATH.value]
        self.is_rule_check_successfull = False
        return msg

      # Create the hasher used to parse file and compute hash
      sha256_hasher = hashlib.sha256()

      # Open file in read binary mode
      with open(rule[Key.PATH.value], 'rb') as file_to_hash:

        # Create the buffer for file reading
        buffer = file_to_hash.read(self.block_size)

        # Iterate the file reading. Each time it loops, it updates the hasher
        # buffer, appending data just read
        while len(buffer) > 0:
          sha256_hasher.update(buffer)
          buffer = file_to_hash.read(self.block_size)

        # Compare the hash to the rule, and set the check flag if needed
        if rule[Key.SHA256.value] != sha256_hasher.hexdigest():
          print("in error")
          self.is_rule_check_successfull = False
          msg = "File " + rule[Key.PATH.value] + " has an invalid SHA256 hash. SHA256 is " + sha256_hasher.hexdigest() + " instead of " + rule[Key.SHA256.value]
        else:
          print("in success")
          msg = "File " + rule[Key.PATH.value] + " has a valid SHA256 hash. hash is " + sha256_hasher.hexdigest()

    # Default exit, return the msg value
    return msg 
