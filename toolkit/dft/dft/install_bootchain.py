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

""" This module implements the functionnalities needed to install the bootchain chain in the
generated rootfs. This chain contains uboot, kernel; initramfs and DTB.
"""

import os
import stat
import logging
import tempfile
from cli_command import CliCommand
from model import Key

#
#    Class Installbootchain
#
class InstallBootChain(CliCommand):
  """This class implements method needed to install the boot chain in the rootfs.

  This chain includes :
    . uboot or grub (depending on architecture)
    . kernel
    . initramfs
    . DTB
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

  # -------------------------------------------------------------------------
  #
  # install_bootchain
  #
  # -------------------------------------------------------------------------
  def install_bootchain(self):
    """This method implement the installation of the bootchain in the
    generated rootfs. The bootchain inludes the kernel itself, uboot,
    dtb files etc.
    """

    # Ensure firmware generation path exists and is a dir
    if not os.path.isdir(self.project.get_rootfs_mountpoint()):
      logging.critical("The rootfs directory does not exist (" +
                       self.project.get_rootfs_mountpoint() + ")")
      exit(1)

    # Check if we are working with foreign arch, then ...
    if self.use_qemu_static:
      # QEMU is used, and we have to install it into the target
      self.setup_qemu()

    # Retrieve the target components (version and board)
    if Key.TARGETS.value in self.project.project[Key.PROJECT_DEFINITION.value]:
      # Iterate the list of targets in order to load th BSP definition file
      for target in self.project.project[Key.PROJECT_DEFINITION.value][Key.TARGETS.value]:
        # Check if the BSP if defined, otherwise there is nothing to do
        if Key.BSP.value in target:
          # Setup the packages sources
          self.setup_kernel_apt_sources(target)
          # Install the kernel packages
          self.install_kernel_apt_packages(target)
        else:
          logging.warning("The '" + Key.BSP.value + "' key is not defined for target '" +
                          target[Key.BOARD.value] + "'")

    else:
      logging.error("The '" + Key.TARGETS.value + "' key is not defined in the project file")
      exit(1)

    # Remove QEMU if it has been isntalled. It has to be done in the end
    # since some cleanup tasks could need QEMU
    if self.use_qemu_static:
      self.cleanup_qemu()



  # -------------------------------------------------------------------------
  #
  # setup_kernel_apt_sources
  #
  # -------------------------------------------------------------------------
  def setup_kernel_apt_sources(self, target):
    """This method implement the installation of the bootchain in the
    generated rootfs. The bootchain inludes the kernel itself, uboot,
    dtb files etc.
    """

    # Output current task to logs
    logging.info("Setting up APT sources for kernel")

    # Generated the base path to the file to create
    filepath = self.project.get_rootfs_mountpoint() + "/etc/apt/sources.list.d/"

    # Control the package provider. So far only handles debian armbian and devuan
    if target[Key.BSP.value][Key.KERNEL.value][Key.ORIGIN.value] not in \
      "devuan" "debian" "armbian" "armwizard" "custom":
      logging.error("Unknown kernel provider '" + target[Key.BSP.value][Key.KERNEL.value]\
                    [Key.ORIGIN.value] + "'")
      exit(1)

    # Check if the provider is Debian, if yes, there is nothing to do for source list generation
    # The system will use the sources defined for rootfs installation
    if target[Key.BSP.value][Key.KERNEL.value][Key.ORIGIN.value] == Key.DEBIAN.value:
      logging.debug("Using Debian repo as source provider.")
    else:
      # Set the repo name to None. It will be checked in the end to know if there is a key
      # to install (key may have be installed using wget instead of apt-key in case of custom repo)
      repo_pub_key = None

      # Target is not Debian, then we need to create a temporary file for source file generation
      # and complete the path according to the known providers
      with tempfile.NamedTemporaryFile(mode='w+', delete=False) as working_file:
        if target[Key.BSP.value][Key.KERNEL.value][Key.ORIGIN.value] == Key.DEVUAN.value:
          # Defines the file name and content for devuan APT sources
          logging.debug("Using Devuan repo as source provider. Adding devuan.list")
          filepath += "devuan_repository.list"
          working_file.write("deb http://packages.devuan.org/devuan ")
          working_file.write(target[Key.VERSION.value])
          working_file.write(" main\n")

          # Check if the public key of the repository is defined in the BSP file, otherwise
          # Set the default value of the key
          if Key.PUBKEY.value not in target[Key.BSP.value][Key.KERNEL.value]:
            repo_pub_key = Key.DEVUAN_SIGNING_PUBKEY.value
            logging.debug("Using default Devuan signing key " + repo_pub_key)
          else:
            repo_pub_key = target[Key.BSP.value][Key.KERNEL.value][Key.PUBKEY.value]
            logging.debug("Add Devuan signing key " + repo_pub_key)

        elif target[Key.BSP.value][Key.KERNEL.value][Key.ORIGIN.value] == Key.ARMBIAN.value:
          # Defines the file name and content for armbian APT sources
          logging.debug("Using Armbian repo as source provider. Adding armbian.list")
          filepath += "armbian_repository.list"
          working_file.write("deb http://apt.armbian.com jessie main utils jessie-desktop\n")

          # Check if the public key of the repository is defined in the BSP file, otherwise
          # Set the default value of the key
          if Key.PUBKEY.value not in target[Key.BSP.value][Key.KERNEL.value]:
            repo_pub_key = Key.ARMBIAN_SIGNING_PUBKEY.value
            logging.debug("Using default Armbian signing key " + repo_pub_key)
          else:
            repo_pub_key = target[Key.BSP.value][Key.KERNEL.value][Key.PUBKEY.value]
            logging.debug("Add Armbian signing key " + repo_pub_key)

        elif target[Key.BSP.value][Key.KERNEL.value][Key.ORIGIN.value] == Key.ARMWIZARD.value:
          # Defines the file name and content for armbian APT sources
          logging.debug("Using ArmWizard repo as source provider. Adding armwizard.list")
          filepath += "armwizard_repository.list"
          working_file.write("deb http://apt.armwizard.org/armwizard " + target[Key.VERSION.value])
          working_file.write(" bsp\n")

          # Check if the public key of the repository is defined in the BSP file, otherwise
          # Set the default value of the key
          if Key.PUBKEY.value not in target[Key.BSP.value][Key.KERNEL.value]:
            repo_pub_key = Key.ARMWIZARD_SIGNING_PUBKEY.value
            logging.debug("Using default Armwizard signing key " + repo_pub_key)
          else:
            repo_pub_key = target[Key.BSP.value][Key.KERNEL.value][Key.PUBKEY.value]
            logging.debug("Add Armbian signing key " + repo_pub_key)

        elif target[Key.BSP.value][Key.KERNEL.value][Key.ORIGIN.value] == Key.CUSTOM.value:
          # Defines the file name and content for custom APT sources
          logging.debug("Using custom repo as source provider. Adding custom_bsp_repository.list")
          filepath += "custom_bsp_repository.list"
          working_file.write("deb " + target[Key.BSP.value][Key.KERNEL.value][Key.URL.value] + "\n")

          # Check if the public key of the repository is defined in the BSP file, otherwise
          # Check if there is a pubkey to retrieve using its url
          if Key.PUBKEY_URL.value in target[Key.BSP.value][Key.KERNEL.value]:
            key_url = target[Key.BSP.value][Key.KERNEL.value][Key.PUBKEY_URL.value]
            logging.debug("retrieving public key : " + key_url)

            # Generate the retrieve and add command
            command = "chroot " + self.project.get_rootfs_mountpoint() + " bash -c "
            command += "'/usr/bin/wget -qO - "
            command += target[Key.BSP.value][Key.KERNEL.value][Key.PUBKEY_URL.value]
            command += " | /usr/bin/apt-key add -'"
            self.execute_command(command)

          # Public key is not available, installation is likely to fail
          else:
            logging.error("No public key is defined in board definition.")
            logging.error("Continuing, but installation of kernel is likely to fail.")

      # Update new source file permissions. It has to be world readable
      os.chmod(working_file.name, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

      # Move the temporary file under the rootfs tree
      command = "mv -f " + working_file.name + " " + filepath
      self.execute_command(command)

      # Add a key to the know catalog signing keys, only if a key fingerprint has been defined
      if not repo_pub_key is None:
        self.add_catalog_signing_key(repo_pub_key)

      # Update the catalog once the new sources is set
      self.update_package_catalog()


  # -------------------------------------------------------------------------
  #
  # install_kernel_apt_packages
  #
  # -------------------------------------------------------------------------
  def install_kernel_apt_packages(self, target):
    """This method implement the installation of the bootchain in the
    generated rootfs. The bootchain inludes the kernel itself, uboot,
    dtb files etc.
    """

    # Output current task to logs
    logging.info("Installing kernel sources")

    # Check that the kernel entry is defined in the BSP
    if Key.KERNEL.value in target[Key.BSP.value]:
      # Check that the packages list is defined under kernel entry
      if Key.PACKAGES.value in target[Key.BSP.value][Key.KERNEL.value]:
        # Iterate the list of packages to install, and install them
        for pkg in target[Key.BSP.value][Key.KERNEL.value][Key.PACKAGES.value]:
          logging.debug("Installing package " + pkg)
          self.install_package(pkg)
      else:
        logging.debug("No package list under kernel. Nothing to do...")
    else:
      logging.debug("No kernel entry in the BSP. Nothing to do...")
