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
      "devuan" "debian" "armbian":
      logging.error("Unknown kernel provider '" + target[Key.BSP.value][Key.ORIGIN.value] + "'")
      exit(1)

    # Check if the provider is Debian, if yes, there is nothing to do for source list generation
    # The system will use the sources defined for rootfs installation
    if target[Key.BSP.value][Key.KERNEL.value][Key.ORIGIN.value] == "debian":
        logging.debug("Using Debian repo as source provider.")
    else:
      # Target is not Debian, then we need to create a temporary file for source file generation
      # and complete the path according to the known providers
      with tempfile.NamedTemporaryFile(mode='w+', delete=False) as working_file:
        if target[Key.BSP.value][Key.KERNEL.value][Key.ORIGIN.value] == "devuan":
          logging.debug("Using Devuan repo as source provider. Adding devuan.list")
          filepath += "devuan.list"
          working_file.write("deb http://packages.devuan.org/devuan ")
          working_file.write(target[Key.VERSION.value])
          working_file.write(" main\n")
        elif target[Key.BSP.value][Key.KERNEL.value][Key.ORIGIN.value] == "armbian":
          logging.debug("Using Armbian repo as source provider. Adding armbian.list")
          filepath += "armbian.list"
          working_file.write("deb http://apt.armbian.com jessie main utils jessie-desktop\n")

      # Finally move the temporary file under the rootfs tree
      sudo_command = "sudo mv -f " + working_file.name + " " + filepath
      print(sudo_command)
      self.execute_command(sudo_command)



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

#    print(target)

# puis install avec un update
# et en itereant sur le saction packages
# ca uniquement si on connait e provider
# pour le moment on en gère que trois
#    self.install_package("xxx")
