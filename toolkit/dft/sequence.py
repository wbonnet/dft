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
import os
from shutil import rmtree
from dft.cli_command import CliCommand
from dft.model import Key

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
  #
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
    found_sequence = False
    for sequence in self.project.project[Key.BUILDING_SEQUENCES.value]:
      if self.dft.sequence_name == sequence[Key.SEQUENCE_NAME.value].lower():
        logging.debug("Found sequence " + self.dft.sequence_name)
        found_sequence = True
        break

    # Was sequence found ?
    if not found_sequence:
      logging.fatal("Sequence " + self.dft.sequence_name + \
                    " was not found in project file. Aborting.")
      exit(1)

    # Check that there is a firmware configuration file first
    if len(sequence) == 0:
      logging.info("Sequence " + self.dft.sequence_name + " is empty. Nothing to do.")
    else:
      for step in sequence[Key.STEPS.value]:
        logging.debug("Doing step : " + step[Key.ACTION.value])

