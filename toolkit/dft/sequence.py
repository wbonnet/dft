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

""" This module contains the functionnalities needed to run a sequence of DFT command
defined in the configuration file. This feature is used to execute in a row the
different steps needed to build a firmware image from scratch.
"""

import logging
from dft.cli_command import CliCommand
from dft.model import Key
from dft import assemble_firmware
from dft import install_bootchain
from dft import build_image
from dft import build_firmware
from dft import build_rootfs
from dft import check_rootfs
from dft import strip_rootfs
from dft import list_content

#
#    Class Sequence
#
class Sequence(CliCommand):
  """This class implements method needed to create the load and run
  sequence of commands
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
  # run_sequence
  #
  # -------------------------------------------------------------------------
  def run_sequence(self):
    """This method implement the business logic of running of sequence of DFT
    command. Command are the same as commands available from the CLI
    (assemble_firmware, build_firmware, build_rootfs, etc.).
    """

    # Check that sequence name has been properly defined in configuration object
    if self.dft.sequence_name is None:
      logging.fatal("The sequence name is not defined in the configuration object. Aborting.")
      exit(1)

    #
    # Retrieve the sequence to process
    #

    # Check there is a project building section
    if Key.BUILDING_SEQUENCES.value not in self.project.project:
      logging.fatal("The project file does not contains any " + Key.BUILDING_SEQUENCES.value + \
                    " section.")
      logging.fatal(Key.BUILDING_SEQUENCES.value + " is where sequences are defined. Aborting.")
      exit(1)

    # Is there only one sequence and no sequence name argument ? If yes default to this sequence
    if self.dft.sequence_name == Key.DEFAULT_SEQUENCE_NAME.value and \
       len(self.project.project[Key.BUILDING_SEQUENCES.value]):
      logging.debug("Defaulting to sequence : " + \
                    self.project.project[Key.BUILDING_SEQUENCES.value][0][Key.SEQUENCE_NAME.value])

    # Then search the sequence by its name. Use a boolean flag to mark it has been found
    sequence = None
    for seq in self.project.project[Key.BUILDING_SEQUENCES.value]:
      if self.dft.sequence_name == seq[Key.SEQUENCE_NAME.value].lower():
        logging.debug("Found sequence " + self.dft.sequence_name)
        sequence = seq
        break

    # Was sequence found ?
    if sequence is None:
      logging.fatal("Sequence " + self.dft.sequence_name + \
                    " was not found in project file. Aborting.")
      exit(1)

    # Check that there is a firmware configuration file first
    if len(sequence) == 0:
      logging.info("Sequence " + self.dft.sequence_name + " is empty. Nothing to do.")
    else:
      # Some steps are defined in the list. Iterate it and call run_tep method on eah step
      for step in sequence[Key.STEPS.value]:
        if not self.execute_step(step):
          logging.error("Execution of step " + step[Key.ACTION.value] + " failed. Aborting")
          exit(1)



  # -------------------------------------------------------------------------
  #
  # execute_step
  #
  # -------------------------------------------------------------------------
  def execute_step(self, step):
    """This method implement the business logic of executing a single step
    from a sequence of commands. Commands are the same as commands available
    from the CLI (assemble_firmware, build_firmware, build_rootfs, etc.).
    """

    # According to the step action, call the method dedicated to execute it
    logging.debug("Executing step : " + step[Key.ACTION.value])

    # Command object used for step processing
    command = None

    # Handle the assemble_firmware action
    if step[Key.ACTION.value] == Key.ASSEMBLE_FIRMWARE.value:
      # Makes a copy of the configuration before applying arguments redefined
      # in the project file (within the sequence of steps)
      cfg = self.copy_config_and_apply_args(step)

      # Create the business object and call the execution method
      command = assemble_firmware.AssembleFirmware(cfg, self.project)
      command.assemble_firmware()

    # Handle the build_rootfs action
    elif step[Key.ACTION.value] == Key.BUILD_ROOTFS.value:
      # Makes a copy of the configuration before applying arguments redefined
      # in the project file (within the sequence of steps)
      cfg = self.copy_config_and_apply_args(step)

      # Create the business object and call the execution method
      command = build_rootfs.BuildRootFS(cfg, self.project)
      command.create_rootfs()

    # Handle the install_bootchain action
    elif step[Key.ACTION.value] == Key.INSTALL_BOOTCHAIN.value:
      # Makes a copy of the configuration before applying arguments redefined
      # in the project file (within the sequence of steps)
      cfg = self.copy_config_and_apply_args(step)

      # Create the business object and call the execution method
      command = install_bootchain.InstallBootChain(cfg, self.project)
      command.install_bootchain()

    # Handle the build_image action
    elif step[Key.ACTION.value] == Key.BUILD_IMAGE.value:
      # Makes a copy of the configuration before applying arguments redefined
      # in the project file (within the sequence of steps)
      cfg = self.copy_config_and_apply_args(step)

      # Create the business object and call the execution method
      command = build_image.BuildImage(cfg, self.project)
      command.build_image()

    # Handle the buid_partitions action
    elif step[Key.ACTION.value] == Key.BUILD_PARTITIONS.value:
      # Makes a copy of the configuration before applying arguments redefined
      # in the project file (within the sequence of steps)
      cfg = self.copy_config_and_apply_args(step)

      # Create the business object and call the execution method
      command = build_image.BuildImage(cfg, self.project)
      command.build_partitions()

    # Handle the build_firmware action
    elif step[Key.ACTION.value] == Key.BUILD_FIRMWARE.value:
      # Create the business object and call the execution method
      command = build_firmware.BuildFirmware(self.dft, self.project)
      command.build_firmware()

    # Handle the check_rootfs action
    elif step[Key.ACTION.value] == Key.CHECK_ROOTFS.value:
      # Makes a copy of the configuration before applying arguments redefined
      # in the project file (within the sequence of steps)
      cfg = self.copy_config_and_apply_args(step)

      # Create the business object and call the execution method
      command = check_rootfs.CheckRootFS(cfg, self.project)
      command.check_rootfs()

    # Handle the content_information action
    elif step[Key.ACTION.value] == Key.CONTENT_INFO.value:
      # Makes a copy of the configuration before applying arguments redefined
      # in the project file (within the sequence of steps)
      cfg = self.copy_config_and_apply_args(step)

      # Create the business object and call the execution method
      command = list_content.ListContent(cfg, self.project)
      command.list_content()

    # Handle the strip_rootfs action
    elif step[Key.ACTION.value] == Key.STRIP_ROOTFS.value:
      # Makes a copy of the configuration before applying arguments redefined
      # in the project file (within the sequence of steps)
      cfg = self.copy_config_and_apply_args(step)

      # Create the business object and call the execution method
      command = strip_rootfs.StripRootFS(cfg, self.project)
      command.strip_rootfs()

    # Handle the unknown action
    else:
      # If the command word is unknown, output an eror, and return false
      logging.fatal("Unknown step action : " + step[Key.ACTION.value] + ". Aborting")
      return False

    # Main exit, still here, this it succeeded
    return True


  # -------------------------------------------------------------------------
  #
  # copy_config_and_apply_args
  #
  # -------------------------------------------------------------------------
  def copy_config_and_apply_args(self, step):
    """This method is used in step processing. It makes a copy of the
    configuration, applies args value from step and returns this copy.

    It is used to passed a modified copy of the configuration to business
    method when xecuting steps, instead of modifying global configuration.
    """

    # Make a copy of the configuration
    cfg = self.dft

    # Iterate the list of arguments if defined
    if Key.ARGUMENTS.value in step and len(step[Key.ARGUMENTS.value]) > 0:
      for arg in step[Key.ARGUMENTS.value]:
        if Key.NAME.value not in arg:
          logging.warning("Name is missing in definition of step " + step[Key.ACTION.value] + \
                          ". Skipping it.")
        else:
          # Process list_content arguents
          cfg.list_all_content = True
          if arg[Key.NAME.value] == Key.OPT_CONTENT_ANTIVIRUS.value:
            cfg.content_antivirus = True
            cfg.list_all_content = False
          elif arg[Key.NAME.value] == Key.OPT_CONTENT_FILES.value:
            cfg.content_files = True
            cfg.list_all_content = False
          elif arg[Key.NAME.value] == Key.OPT_CONTENT_PACKAGES.value:
            cfg.content_packages = True
            cfg.list_all_content = False
          elif arg[Key.NAME.value] == Key.OPT_CONTENT_ROOTKIT.value:
            cfg.content_packages = True
            cfg.list_all_content = False
          elif arg[Key.NAME.value] == Key.OPT_CONTENT_SECURITY.value:
            cfg.dft.content_security = True
            cfg.list_all_content = False
          elif arg[Key.NAME.value] == Key.OPT_CONTENT_VULNERABILITIES.value:
            cfg.content_vulnerabilities = True
            cfg.list_all_content = False
          # Process common arguments
          elif arg[Key.NAME.value] == Key.OPT_KEEP_BOOTSTRAP_FILES.value:
            cfg.keep_bootstrap_files = True
          elif arg[Key.NAME.value] == Key.OPT_OVERRIDE_DEBIAN_MIRROR:
            logging.warning("Debian mirror is not yet overriden. Skipping it...")
    # Returns the modified (or not) copy
    return cfg
