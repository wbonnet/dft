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

""" This modules implements the functionnalities used to strip a rootfs (or rootfs)
according to the rules defined in a Yaml configuration file. Stripping a rootfs is made
of removing files and packages.
"""

import os
import errno
from shutil import rmtree
from dft.enumkey import Key
from dft.cli_command import CliCommand

#
#    Class StripRootFS
#
class StripRootFS(CliCommand):
  """This class implements the methods needed to strip the base OS

  Stripping the base OS is the task to remove extra packages and files
  that should not be included inthe firmware. These files may come from
  different sources (istalled packages, manual creation, etc.)
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
    CliCommand.__init__(self, dft, project)

    # Initialize a dictionnary to hold the list of installed packages
    self.installed_packages = {}

    # Flag to used to keep track of the need to uninstall APT in case wehad to install it
    self.need_to_strip_apt = False



  # -------------------------------------------------------------------------
  #
  # strip_rootfs
  #
  # -------------------------------------------------------------------------
  def strip_rootfs(self):
    """This method implement the business logic of rootfs stripping.

    It calls dedicated method for each step. The main steps are :
    . strip_packages      This step will remove each package marked as absent
    . strip_files         This step will remove each file marked as absent
    . empty_files         This step will truncate each file marked as empty
    . empty_directories   This step will remove content of each directory
                          marked as empty
    """

    # Check if we are working with foreign arch, then ...
    if self.use_qemu_static:
      # QEMU is used, and we have to install it into the target
      self.setup_qemu()

    # Check that there is a stripping definition
    if self.project.stripping is None:
      self.project.logging.info("The project has no stripping information defined")
      return

    # Iterate the list of rule set, and call the dedicated method
    for rules in self.project.stripping:

      # Display startup mesage if defined
      if Key.MESSAGE_START.value in rules:
        self.project.logging.info(rules[Key.MESSAGE_START.value])

      #
      # Strip the differents object categories one by one
      #
      self.strip_packages(rules)
      self.strip_files(rules)
      self.strip_directories(rules)

      # Display end mesage if defined
      if Key.MESSAGE_END.value in rules:
        self.project.logging.info(rules[Key.MESSAGE_END.value])

    # Remove QEMU if it has been isntalled. It has to be done in the end
    # since some cleanup tasks could need QEMU
    if self.use_qemu_static:
      self.cleanup_qemu()

# Then strip the symlinks ??? check it is in unit test



  # -------------------------------------------------------------------------
  #
  # strip_packages
  #
  # -------------------------------------------------------------------------
  def strip_packages(self, rules):
    """This method implement the package stripping

    The method parses the output of the dpkg -l command and checks if packages are
    in the rules dictionnaries, then apply the action defined in the matching rule.
    """

    # Check that the stripping definition includes packages
    if Key.PACKAGES.value in rules:
      # Check that the stripping definition includes a status absent
      if Key.ABSENT.value in rules[Key.PACKAGES.value]:
        # Retrieve the list of installed packages
        command = "LANG=C chroot " + self.project.get_rootfs_mountpoint()
        command += " dpkg -l | tail -n +6 | awk '{ print $2 }'"
        pkglist = self.execute_command(command)

        # Transform the binary outputinto text
        for binaryline in pkglist.splitlines():
          # Each fields is stored into a variable to easy manipulation and
          # simplify code. First get the array of words converted to UTF-8
          self.installed_packages[binaryline.decode('utf-8').split()[0]] = True

        # Iterate the list packages to remove
        for pkg in rules[Key.PACKAGES.value][Key.ABSENT.value]:
          # If the package is installed
          if pkg in self.installed_packages:
            # First chck if we h&ve to add APT
            filepath = self.project.get_rootfs_mountpoint() + "/usr/bin/apt-get"

            # Test if the binary exists
            if not os.path.isfile(filepath):
              # No thus install, and set the flag to mark it has to be removed in the end
              self.project.logging.debug("apt package is needed for tripping, installing it")
              self.install_package("apt")
              self.need_to_strip_apt = True

            # Then remove the package since it is in the kill list !
            self.remove_package(pkg)
      else:
        self.project.logging.debug("The stripping definition does not include packages to remove")
    else:
      self.project.logging.debug("The stripping definition does not include packages section")

    # Package stripping is done, we no longer apt package (if we had to install it)
    # It is now time to remove it. It has to do done before files and directories stripping
    # In case the next stripping stages breaks APT
    if self.need_to_strip_apt:
      self.project.logging.debug("apt package has been installed during stripping, now removing it")
      self.remove_package("apt")

  # -------------------------------------------------------------------------
  #
  # strip_files
  #
  # -------------------------------------------------------------------------
  def strip_files(self, rules):
    """This method implement the file stripping

    The method parses the list of rules, then apply the action defined in the matching rule.
    """

    # Check that the stripping definition includes files
    if Key.FILES.value in rules:
      # Check that the stripping definition includes a status absent
      if Key.ABSENT.value in rules[Key.FILES.value]:
        for working_file in rules[Key.FILES.value][Key.ABSENT.value]:
          self.remove_file(working_file)
      else:
        self.project.logging.debug("The stripping definition does not include files to remove")

      # Check that the stripping definition includes a status empty
      if Key.EMPTY.value in rules[Key.FILES.value]:
        for working_file in rules[Key.FILES.value][Key.EMPTY.value]:
          self.empty_file(working_file)
      else:
        self.project.logging.debug("Stripping definition does not include files to truncate")

    else:
      self.project.logging.debug("Stripping definition does not include files section")

  # -------------------------------------------------------------------------
  #
  # strip_directories
  #
  # -------------------------------------------------------------------------
  def strip_directories(self, rules):
    """This method implement the directory stripping

    The method parses the list of rules, then apply the action defined in the matching rule.
    """

    # Check that the stripping definition includes directories
    if Key.DIRECTORIES.value in rules:
      # Check that the stripping definition includes a status absent
      if Key.ABSENT.value in rules[Key.DIRECTORIES.value]:
        for directory in rules[Key.DIRECTORIES.value][Key.ABSENT.value]:
          self.remove_directory(directory)
      else:
        self.project.logging.debug("Stripping definition does not include directories to remove")

      # Check that the stripping definition includes a status empty
      if Key.EMPTY.value in rules[Key.DIRECTORIES.value]:
        for directory in rules[Key.DIRECTORIES.value][Key.EMPTY.value]:
          self.empty_directory(directory)
      else:
        self.project.logging.debug("The stripping definition does not include files to empty")

    else:
      self.project.logging.debug("The stripping definition does not include directories section")



  # -------------------------------------------------------------------------
  #
  # remove_file
  #
  # -------------------------------------------------------------------------
  def remove_file(self, target):
    """This method removes a file from the target rootfs.
    """

    self.project.logging.debug("Remove file : " + target)

    # Deleting file is done from host rootf. There is no need to trigger a chroot to rm rm
    # Moreover, some files may be missing from the chroot to be target to run chroot
    target = self.project.get_rootfs_mountpoint() + "/" + target
    try:
      os.remove(target)

    # Catch OSError in case of file removal error
    except OSError as err:
      # If file does not exit errno value will be ENOENT
      if err.errno != errno.ENOENT:
        # Thus if excption was caused by something else, throw it upward
        raise



  # -------------------------------------------------------------------------
  #
  # empty_file
  #
  # -------------------------------------------------------------------------
  def empty_file(self, target):
    """This method makes 'empty' a file from the target rootfs. The operation
    is a file truncate.
    """

    self.project.logging.debug("Empty file : " + target)

    # Deleting file is done from host rootf. There is no need to trigger a chroot to rm rm
    # Moreover, some files may be missing from the chroot to be target to run chroot
    target = self.project.get_rootfs_mountpoint() + "/" + target

    # Test if the fileexist before trying to trucate it
    command = "bash -c '[ -f " + target + " ] && truncate " + target
    command += " --size 0 || true'"
    self.execute_command(command)



  # -------------------------------------------------------------------------
  #
  # remove_directory
  #
  # -------------------------------------------------------------------------
  def remove_directory(self, target):
    """This method removes  a directory from the target rootfs.

    This operation also removes recursivly the directory content (thus you'd
    better not remove / ...).
    """

    # Deleting directories is done from host rootfs. There is no need to
    # trigger a chroot to rm. Moreover, some files may be missing from the
    # chroot to be able to run chroot command
    target = self.project.get_rootfs_mountpoint() + "/" + target

    # Check if the directory exist
    if os.path.isdir(target):
      # Yes, then remove it and log it
      rmtree(target)
      self.project.logging.debug("Removed directory " + target)
    else:
      self.project.logging.debug("Directory " + target + " does not exist")




  # -------------------------------------------------------------------------
  #
  # empty_directory
  #
  # -------------------------------------------------------------------------
  def empty_directory(self, target):
    """This method removes a directory content recursivly. Only files and
    symlinks are remove. The sub directories structure is not mdified.
    """

    # Emptying directories is done from host rootf. There is no need to trigger a chroot to rm rm
    # Moreover, some files may be missing from the chroot to be target to run chroot
    target = self.project.get_rootfs_mountpoint() + "/" + target
    self.project.logging.debug("Empty directory : " + target)

    # Check if the target directory exist
    if os.path.isdir(target):
      # Yes thus then we can process it. First retrieve the list en entries
      # in the foler to clean
      for file in os.listdir(target):
        # Get the full path name
        filepath = os.path.join(target, file)
        try:
          # Check if it is a file or a symlink
          if os.path.isfile(filepath) or os.path.islink(filepath):
            # Yes then delete it
            print("os.unlink(" + filepath + ")")
          # Is it a sub directory ?
          elif os.path.isdir(filepath):
            # Yes then recurse it
            self.empty_directory(filepath)
        # Catch any exception that may occur and print the error
        except OSError as err:
          print(err)
    else:
      self.project.logging.debug("Directory " + target + " does not exist")
