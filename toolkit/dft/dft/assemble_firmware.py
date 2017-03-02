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

""" This modules implements the functionnalities used to create the initramfs in charge of
setting up the firmware in memory at system boot.
"""

import logging
import os
import tempfile
from cli_command import CliCommand

#
#    Class AssembleFirmware
#
class AssembleFirmware(CliCommand):
  """This class implements method needed to assemble the toolchain used to
  assemble firmware inmemory when system is booting.

  Firmware assembling incudes the tasks of generating configuration files
  for sqashfs stacking and initramfs generation. It also includes the
  creation of the script used to handles reboot to preious version, and
  integrity check at start.
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
  # assemble_firmware
  #
  # -------------------------------------------------------------------------
  def assemble_firmware(self):
    """This method implement the business logic of firmware assembling.

    Assembling a firmware, use as input the firmware file created from a
    baseos and then generate the configuration files used to loading after
    booting. The configuration is used to define how the filesystems are
    stacked, what should be the physical partitionning, ciphering, etc.

    It calls dedicated method for each step. The main steps are :
    .
    """

    # Ensure firmware generation path exists and is a dir
    if not os.path.isdir(self.project.firmware_directory):
      os.makedirs(self.project.firmware_directory)

    # Ensure firmware exists
    # TODO : iterate the list of squashfs files
    if not os.path.isfile(self.project.firmware_filename):
      logging.critical("The firmware does not exist (" +
                       self.project.firmware_filename + ")")
      exit(1)
  
    # Remove existing initscript if needed
    if os.path.isfile(self.project.init_filename):
      os.remove(self.project.init_filename)

    # Copy the init script to the target directory

    # Generate the stacking script
    self.generate_stack_script()



  # -------------------------------------------------------------------------
  #
  # generate_stack_script
  #
  # -------------------------------------------------------------------------
  def generate_stack_script(self):
    """This method implement the generation of the stacking script

    The stacking script is called in the initramfs by the init script. Stacking
    script is a shell scipt generated using the firmware.yml configuration
    as input. It provides th specific cod used to mount and stack the filesystms
    (using aufs or overlayfs). 
    """

    # Generate the stacking script
        # configuration, then move  roles to the target rootfs
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as working_file:
      # Generate file header
      working_file.write("#\n")
      working_file.write("# This script is in charge of tacking the differnt items of the firmware.\n")
      working_file.write("#\n")
      working_file.write("# Generation date : TODO\n")
      working_file.write("#\n")
      working_file.write("\n")

    # We are done with file generation, close it now
    working_file.close()

    # Generate the file path
    filepath = self.project.stacking_script_filename

    # Finally move the temporary file under the rootfs tree
    sudo_command = "mv -f " + working_file.name + " " + filepath
    self.execute_command(sudo_command)
