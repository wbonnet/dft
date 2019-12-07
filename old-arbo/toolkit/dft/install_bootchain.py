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
# Copyright 2016 DFT project (http://www.firmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
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
from dft.cli_command import CliCommand
from dft.enumkey import Key

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
          # Check that the kernel entry is defined in the BSP
          if Key.KERNEL.value in target[Key.BSP.value]:
            # Setup the packages sources
            self.setup_kernel_apt_sources(target[Key.BSP.value][Key.KERNEL.value], \
                                          target[Key.VERSION.value])
            # Install the kernel packages
            self.install_kernel_apt_packages(target[Key.BSP.value][Key.KERNEL.value])
          else:
            logging.debug("No kernel entry in the BSP. Nothing to do...")
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
  # cleanup
  #
  # -------------------------------------------------------------------------
  def cleanup(self):
    """This method is in charge of cleaning the environment in cqse of errors
    It is mainly umounting the image and removing the losetup mount.
    The generated image is left for post mortem anaysis.
    """
    self.project.logging.info("starting to cleanup")
