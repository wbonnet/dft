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

""" This modules implements the functionnalities used to strip a baseos (or rootfs)
according to the rules defined in a Yaml configuration file. Stripping a baseos is made
of removing files and packages.
"""

from cli_command import CliCommand

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



  # -------------------------------------------------------------------------
  #
  # strip_rootfs
  #
  # -------------------------------------------------------------------------
  def strip_rootfs(self):
    """This method implement the business logic of rootfs stripping.

    TODO
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
    if self.project.stripping_definition is None:
      self.project.logging.info("The project has no stripping information defined")
      return

    #
    # Strip the packages
    #

    # Check that the stripping definition includes packages
    if "packages" in self.project.stripping_definition:
      # Check that the stripping definition includes a status absent
      if "absent" in self.project.stripping_definition["packages"]:
        # Retrieve the list of installed packages
        sudo_command = "LANG=C sudo chroot " + self.project.rootfs_mountpoint
        sudo_command += " dpkg -l | tail -n +6 | awk '{ print $2 }'"
        pkglist = self.execute_command(sudo_command)

        # Transform the binary outputinto text
        for binaryline in pkglist.splitlines():
          # Each fields is stored into a variable to easy manipulation and
          # simplify code. First get the array of words converted to UTF-8
          self.installed_packages[binaryline.decode('utf-8').split()[0]] = True

        # Iterate the list packages to remove
        for pkg in self.project.stripping_definition["packages"]["absent"]:
          # If the package is installed
          if pkg in self.installed_packages:
            # Then remove it !
            self.remove_package(pkg)
      else:
        self.project.logging.debug("The stripping definition does not include packages to remove")
    else:
      self.project.logging.debug("The stripping definition does not include packages section")

    #
    # Strip the files
    #

    # Check that the stripping definition includes files
    if "files" in self.project.stripping_definition:
      # Check that the stripping definition includes a status absent
      if "absent" in self.project.stripping_definition["files"]:
        for working_file in self.project.stripping_definition["files"]["absent"]:
          self.remove_file(working_file)
      else:
        self.project.logging.debug("The stripping definition does not include files to remove")

      # Check that the stripping definition includes a status empty
      if "empty" in self.project.stripping_definition["files"]:
        for working_file in self.project.stripping_definition["files"]["empty"]:
          self.empty_file(working_file)
      else:
        self.project.logging.debug("Stripping definition does not include files to truncate")

    else:
      self.project.logging.debug("Stripping definition does not include files section")

    #
    # Strip the directories
    #

    # Check that the stripping definition includes directories
    if "directories" in self.project.stripping_definition:
      # Check that the stripping definition includes a status absent
      if "absent" in self.project.stripping_definition["directories"]:
        for directory in self.project.stripping_definition["directories"]["absent"]:
          self.remove_directory(directory)
      else:
        self.project.logging.debug("Stripping definition does not include directories to remove")

      # Check that the stripping definition includes a status empty
      if "empty" in self.project.stripping_definition["directories"]:
        for directory in self.project.stripping_definition["directories"]["empty"]:
          self.empty_directory(directory)
      else:
        self.project.logging.debug("The stripping definition does not include files to empty")

    else:
      self.project.logging.debug("The stripping definition does not include directories section")

    # Remove QEMU if it has been isntalled. It has to be done in the end
    # since some cleanup tasks could need QEMU
    if self.use_qemu_static:
      self.cleanup_qemu()




    # First strip the packages
#    need_to_strip_apt = False

    # Check if at some time the APT stuff has be caimed for removal
 #   if need_to_strip_apt:
      # We now have to remove
  #    pass
# Next strip the directories
# Then strip the symlinks
# And finally strip the files

  # -------------------------------------------------------------------------
  #
  # remove_package
  #
  # -------------------------------------------------------------------------
  def remove_package(self, target):
    """This method deinstall a package from the target rootfs, and purge its
    configuration file. It will remove anything necessary to prevent having
    packages in the 'rc' state.

    This command is executed inside the chrooted environment and may need to
    have qemu installed.
    """

    self.project.logging.debug("Remove package : " + target)
    sudo_command = "sudo chroot " + self.project.rootfs_mountpoint
    sudo_command += " /usr/bin/apt-get remove " + target
    self.execute_command(sudo_command)



  # -------------------------------------------------------------------------
  #
  # remove_file
  #
  # -------------------------------------------------------------------------
  def remove_file(self, target):
    """This method removes a file from the target rootfs.

    For safety reasons, this command is executed inside the chrooted
    environment and may need to have qemu installed.
    """

    self.project.logging.debug("Remove file : " + target)
    sudo_command = "sudo chroot " + self.project.rootfs_mountpoint
    sudo_command += " rm -f " + target
    self.execute_command(sudo_command)



  # -------------------------------------------------------------------------
  #
  # empty_file
  #
  # -------------------------------------------------------------------------
  def empty_file(self, target):
    """This method makes 'empty' a file from the target rootfs. The operation
    is a file truncate.

    For safety reasons, this command is executed inside the chrooted
    environment and may need to have qemu installed.
    """

    self.project.logging.debug("Empty file : " + target)

    # Test if the fileexist before trying to trucate it
    sudo_command = "sudo chroot " + self.project.rootfs_mountpoint
    sudo_command += " bash -c '[ -f " + target + " ] && truncate " + target
    sudo_command += " --size 0'"
    self.execute_command(sudo_command)



  # -------------------------------------------------------------------------
  #
  # remove_directory
  #
  # -------------------------------------------------------------------------
  def remove_directory(self, target):
    """This method removes  a directory from the target rootfs.

    This operation also rmoves recursivly the directory content (thus you'd
    better not remove / ...).

    For safety reasons, this command is executed inside the chrooted
    environment and may need to have qemu installed.
    """

    self.project.logging.debug("Remove directory : " + target)
    sudo_command = "sudo chroot " + self.project.rootfs_mountpoint
    sudo_command += " rm -fr " + target
    self.execute_command(sudo_command)



  # -------------------------------------------------------------------------
  #
  # empty_directory
  #
  # -------------------------------------------------------------------------
  def empty_directory(self, target):
    """This method removes a dirctory content recursivly. Only files and
    symlinks are remove. The sub dirctories structure is not mdified.

    For safety reasons, this command is executed inside the chrooted
    environment and may need to have qemu installed.
    """

    self.project.logging.debug("Empty directory : " + target)
